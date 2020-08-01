#!/usr/bin/env bash

# more bash-friendly output for jq
JQ="jq --raw-output --exit-status"
echo "What is this $1"
#staging.location-tracker.
get_env(){
 echo $(aws ssm get-parameters --names $CIRCLE_BRANCH.$PROJECT_NAME.$1 \
          --with-decryption --region $AWS_REGION --output json | \
          $JQ '.Parameters[].Value')
}


###################
# AVAILABLE VARS  #
###################

# AWS_ACCOUNT_ID
# AWS_REGION
# $BRANCH_NAME

###################
#   FIXED VARS    #
###################


PROJECT_NAME="favorite-backend"
FAMILY=$PROJECT_NAME


if [[ $CIRCLE_BRANCH == "develop" ]] ; then
    AWS_REGION="us-west-2"
	CIRCLE_BRANCH="develop" 
    ENV="develop"
    LOG_GROUP="develop-$PROJECT_NAME"
    FAMILY=$FAMILY"_develop"
    CLUSTER="develop"
elif [[ $CIRCLE_TAG == "master."* ]] ; then
    AWS_REGION="us-west-2"
	CIRCLE_BRANCH="master" 
    ENV="prod"
    SETTINGS="voyage_control.settings.production_docker"
    LOG_GROUP="production-$PROJECT_NAME"
    CLUSTER="master"

fi


###################
#    ENV VARS     #
###################

CPU_SHARES=$(get_env "cpu_shares") ;{echo ${CPU_SHARES:=256}} 2> /dev/null
MEM_SHARES=$(get_env "mem_shares") ;{echo ${MEM_SHARES:=256}} 2> /dev/null
CONTAINER_PORT=$(get_env "container_port") ;{echo ${CONTAINER_PORT:=5000}} 2> /dev/null

DATABASE_URL=$(get_env "db_url")

make_task_def() {
	echo '[
		{
			"name": "'$PROJECT_NAME'",
			"image": "'$AWS_ACCOUNT_ID'.dkr.ecr.'$AWS_REGION'.amazonaws.com/'$PROJECT_NAME':'$CIRCLE_BRANCH'-'$CIRCLE_BUILD_NUM'",
			"essential": true,
			"memoryReservation": '$MEM_SHARES',
			"cpu": '$CPU_SHARES',
			"portMappings": [
				{
					"containerPort": '90'
				}
			],
			"privileged": true,
			"environment" :[
				{
					"name":"ENV",
					"value":"'$ENV'"
				},
				{
					"name":"PORT",
					"value":"'90'"
				},
				{
					"name":"DATABASE_URL",
					"value":"'$DATABASE_URL'"
				}
			]
		}
	]'
}

configure_aws_cli(){
	aws --version
	aws configure set default.region $AWS_REGION
	aws configure set default.output json
}

build_ecr_image(){
	docker build -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$PROJECT_NAME:$CIRCLE_BRANCH-$CIRCLE_BUILD_NUM .
	docker tag $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$PROJECT_NAME:$CIRCLE_BRANCH-$CIRCLE_BUILD_NUM $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$PROJECT_NAME:$CIRCLE_BRANCH
}

push_ecr_image(){
	eval $(aws ecr get-login --region $AWS_REGION --no-include-email)
	docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$PROJECT_NAME:$CIRCLE_BRANCH-$CIRCLE_BUILD_NUM 
}

register_definition() {
  task_def=$(make_task_def)
	echo "$task_def"
	echo "Task definition created"

  if revision=$(aws ecs register-task-definition --container-definitions "$task_def" --family "$FAMILY" | \
                  $JQ '.taskDefinition.taskDefinitionArn'); then
    echo "Revision: $revision"
  else
    echo "Failed to register task definition"
    return 1
  fi
}

deploy_cluster() {
  if [[ $(aws ecs update-service --cluster "$CLUSTER" --service "$PROJECT_NAME" --task-definition "$revision" | \
                   $JQ '.service.taskDefinition') != $revision ]]; then
        echo "Error updating service."
        return 1
	fi

	echo "Deployed!"
	return 0
}

configure_aws_cli
build_ecr_image
push_ecr_image
register_definition
deploy_cluster

