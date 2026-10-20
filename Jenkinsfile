pipeline {
    agent any

    options {
        timestamps()
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
    }

    environment {
        // Resolve Python from the Jenkins agent's PATH instead of using a
        // developer-specific installation path.
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
                bat """
                    where %PYTHON%
                    %PYTHON% --version
                    if not exist %REPORT_DIR% mkdir %REPORT_DIR%
                    %PYTHON% -m venv .jenkins-venv
                    %CI_PYTHON% -m pip install --upgrade pip
                    %CI_PYTHON% -m pip install -r requirements.txt -r requirements-build.txt
                    %CI_PYTHON% -m build --wheel --no-isolation helper
                    %CI_PYTHON% -m pip install --no-deps helper\\dist\\alert_helper-0.1.0-py3-none-any.whl
                    %CI_PYTHON% -m pip install bandit pip-audit
                """
            }
        }

        stage("Static Security Scan") {
            steps {
                bat """
                    %CI_PYTHON% -m bandit -r app -f json -o %REPORT_DIR%\\bandit.json --exit-zero
                    %CI_PYTHON% -m bandit -r app -f screen --exit-zero > %REPORT_DIR%\\bandit.txt
                """
            }
        }

        stage("Dependency Audit") {
            steps {
                bat """
                    %CI_PYTHON% -m pip_audit -r requirements.txt --cache-dir .pip-audit-cache -f json -o %REPORT_DIR%\\pip-audit.json
                """
            }
        }

        stage("Security Gate") {
            steps {
                bat """
                    rem Fail the build when Bandit reports high-severity findings.
                    %CI_PYTHON% -m bandit -r app -lll
                """
            }
        }

        stage("Tests") {
            steps {
                bat """
                    %CI_PYTHON% tests\\test_store_sql.py > %REPORT_DIR%\\test_store_sql.txt 2>&1
                    %CI_PYTHON% tests\\test_flow.py > %REPORT_DIR%\\test_flow.txt 2>&1
                """
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: "reports/**", allowEmptyArchive: true
            archiveArtifacts artifacts: "**/junit-*.xml", allowEmptyArchive: true
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
