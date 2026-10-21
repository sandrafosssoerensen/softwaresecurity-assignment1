pipeline {
    agent any

    options {
        timestamps()
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
    }

    environment {
        PYTHON = "python"
        CI_PYTHON = ".jenkins-venv\\Scripts\\python.exe"
        REPORT_DIR = "reports"
    }

    triggers {
        githubPush()
    }

    stages {
        stage("Checkout") {
            steps {
                deleteDir()
                checkout scm
            }
        }

        stage("Build") {
            steps {
                // Separate steps ensure every failed build command stops Jenkins.
                bat 'where %PYTHON%'
                bat '%PYTHON% --version'
                bat 'if not exist "%REPORT_DIR%" mkdir "%REPORT_DIR%"'
                bat '%PYTHON% scripts\\check_dependencies.py --validate-only'
                bat '%PYTHON% -m venv .jenkins-venv'
                bat '"%CI_PYTHON%" -m pip install -r requirements.txt -r requirements-build.txt -r requirements-ci.txt'
                bat '"%CI_PYTHON%" -m build --wheel --no-isolation helper'
                bat '"%CI_PYTHON%" -m pip install --no-deps helper\\dist\\alert_helper-0.1.0-py3-none-any.whl'
                bat '"%CI_PYTHON%" -m pip check'
            }
        }

        stage("Dependency Approval") {
            steps {
                bat '"%CI_PYTHON%" scripts\\check_dependencies.py --report "%REPORT_DIR%\\dependency-approval.json"'
            }
        }

        stage("Static Security Scan") {
            steps {
                bat '"%CI_PYTHON%" -m bandit -r app -f json -o "%REPORT_DIR%\\bandit.json" --exit-zero'
                bat '"%CI_PYTHON%" -m bandit -r app -f screen --exit-zero > "%REPORT_DIR%\\bandit.txt"'
            }
        }

        stage("Dependency Audit") {
            steps {
                bat '"%CI_PYTHON%" -m pip_audit -r requirements.txt --cache-dir .pip-audit-cache -f json -o "%REPORT_DIR%\\pip-audit.json"'
            }
        }

        stage("Security Gate") {
            steps {
                bat '"%CI_PYTHON%" -m bandit -r app -lll'
            }
        }

        stage("Tests") {
            steps {
                script {
                    // Run every suite to preserve evidence, then fail if ANY failed.
                    def approvalStatus = bat(returnStatus: true, script: '"%CI_PYTHON%" tests\\test_dependency_gate.py > "%REPORT_DIR%\\test_dependency_gate.txt" 2>&1')
                    def sqlStatus = bat(returnStatus: true, script: '"%CI_PYTHON%" tests\\test_store_sql.py > "%REPORT_DIR%\\test_store_sql.txt" 2>&1')
                    def flowStatus = bat(returnStatus: true, script: '"%CI_PYTHON%" tests\\test_flow.py > "%REPORT_DIR%\\test_flow.txt" 2>&1')
                    if (approvalStatus != 0 || sqlStatus != 0 || flowStatus != 0) {
                        error("Required tests failed: approval=" + approvalStatus + ", SQL=" + sqlStatus + ", HTTP=" + flowStatus)
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: "reports/**", allowEmptyArchive: true
            deleteDir()
        }
        success {
            echo "Secure build and tests passed."
        }
        failure {
            echo "Build blocked: inspect the archived security or test reports."
        }
    }
}
