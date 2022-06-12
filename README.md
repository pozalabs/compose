# python-project-template
파이썬 프로젝트 템플릿

## 프로젝트 설정

1. 파이썬 버전 설정 (pyenv, ...)
   - 현재 파이썬 버전: **3.9 (3.9.11+)**
   - 현재 파이썬 버전이 적절한 버전인지, 다른 가상 환경이 실행 중인건 아닌지 반드시 확인해야 합니다.
2. 스크립트 실행
   ```shell
   $ source ./scripts/setup-project.sh
   ```
   - 스크립트 종료 후 생성한 가상 환경을 유지하기 위해 `source` 명령어를 사용합니다.
   - 스크립트는 아래 단계를 수행합니다.
     1. 파이썬 가상 환경 생성 및 실행 (`<CURRENT_DIR>/.venv`)
     2. poetry 프로젝트 생성
     3. 파이썬 패키지 생성
        - 스크립트에서 입력을 요구하므로 적절한 패키지명을 입력합니다. (아래 예시를 참고하세요.)
        ```shell
        $ Initialized project with poetry
        $ Added pre-commit configurations
        $ Installing pre-commit 
        $ pre-commit installed at .git/hooks/pre-commit 
        $ Installed pre-commit 
        $ Poetry setup finished 
        $ Type package name. This will create python package with <PACKAGE_NAME>
        $ src << 입력한 패키지명 
        $ Created python package named src
        ```
