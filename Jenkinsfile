    agent {
        label 'build.dev.cloud.im'
    }
    environment {
        PACKAGE_TYPE="zip"

        SEMANTIC_VERSION=sh(returnStdout: true, script: "git describe --abbrev=0 --tags || echo 'v0.0.0-dev'").trim()

        PROJECT_NAME="adobe-reports"
        PROJECT_KEY="connectors-${PROJECT_NAME}"
        PROJECT_VERSION="${SEMANTIC_VERSION}" + "${SEMANTIC_VERSION == 'v0.0.0-dev' ? '.' : '-'}" + "${BUILD_NUMBER}"
        PROJECT_DELIVERABLE="${PROJECT_NAME}-${PROJECT_VERSION}.${PACKAGE_TYPE}"

        STORAGE_PATH="/home/storage/connect/${PROJECT_NAME}"
        STORAGE_HOST="storage.dev.cloud.im"

        HAS_PYPROJECT_FILE = fileExists 'pyproject.toml'
        HAS_REQUIREMENTS_FILE = fileExists 'requirements.txt'
    }
    stages {
        stage('Environment Setup') {
            steps {
                sh """
                /usr/local/bin/python3.8 -m venv venv
                source venv/bin/activate

                pip install --upgrade pip
                pip install pylint poetry --trusted-host pypi.int.zone
                poetry check
                poetry env info
                poetry config virtualenvs.create false
                poetry install
                """
            }
        }
        stage('Test Execution') {
            steps {
                sh """
                source venv/bin/activate
                poetry run pytest -p no:cacheprovider --cov=reports --cov-report xml
                """
            }
        }
        stage('SonarQube Analysis') {
            steps {
                script {
                    def SCANNER_HOME = tool name: 'SonarQubeIntZoneScanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation';
                    withSonarQubeEnv('SonarQubeIntZone') {
                        sh """
                        export JAVA_HOME=/usr/lib/jvm/java-11-openjdk
                        ${SCANNER_HOME}/bin/sonar-scanner \
                        -Dsonar.project.tags=connectors \
                        -Dsonar.projectVersion=${PROJECT_VERSION} \
                        -Dsonar.projectKey=${PROJECT_KEY} \
                        -Dsonar.sources=reports \
                        -Dsonar.tests=tests/ \
                        -Dsonar.python.coverage.reportPaths=coverage.xml \
                        -Dsonar.python.pylint=venv/bin/pylint
                        """
                    }
                }
            }
        }
        stage ('Build Package') {
            steps {
                sh """
                zip -r "${PROJECT_DELIVERABLE}" . -x "vendor/*" ".git/*" ".gitignore" "Jenkinsfile" "tests/*" ".scannerwork/*" "venv/*" ".pytest_cache/*" "*coverage*" "*__pycache__*" "htmlcov/*"
                stat "${PROJECT_DELIVERABLE}"
                """
            }
        }
        stage('Publish Package') {
            when {
                allOf {
                    branch "master"
                    expression {
                        return (SEMANTIC_VERSION != "v0.0.0-dev")
                    }
                }
            }
            steps {
                sh """
                ssh storage@${STORAGE_HOST} "[ -d ${STORAGE_PATH} ] ||  mkdir -p ${STORAGE_PATH}"
                scp "${PROJECT_DELIVERABLE}" storage@${STORAGE_HOST}:${STORAGE_PATH}/${PROJECT_DELIVERABLE}
                echo "Link to download the package: http://${STORAGE_HOST}:81/connect/${PROJECT_NAME}/${PROJECT_DELIVERABLE}"
                """
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}