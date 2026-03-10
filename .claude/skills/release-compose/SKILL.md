---
name: release-compose
description: compose 패키지 버전 업데이트, 변경 내역 작성 및 릴리즈 배포
allowed-tools: Bash(git:*), Bash(gh:*), Bash(linear:*), Bash(sed:*), Skill, Read, Edit, Write
argument-hint: "<version>"
---

# compose Release

compose 패키지의 버전 업데이트, 변경 내역(CHANGELOG.md) 작성, PR 생성/머지, Draft 릴리즈 배포를 수행한다.

## Git 컨텍스트

- repo: !`git remote get-url origin | sed 's|.*github.com[:/]||' | sed 's|\.git$||'`
- default-branch: !`git rev-parse --abbrev-ref origin/HEAD | sed 's|origin/||'`
- current-branch: !`git branch --show-current`

## 인자

- `<version>`: 배포할 버전 (형식: `v{major}.{minor}.{patch}`)
- `--skip-sync`: release 브랜치 동기화 단계 건너뛰기

**사용자 입력 인자**: $ARGUMENTS

## 실행 단계

### 사전 검증

1. **버전 인자 검증**
   - 버전 인자가 없으면 에러 메시지 출력 후 종료
   - `v` 접두사가 없으면 자동 추가

2. **버전 유효성 확인**
   - `pyproject.toml`의 `version` 필드에서 현재 버전 확인
   - 입력된 버전이 현재 버전 이하이면 에러 메시지 출력 후 AskUserQuestion으로 올바른 버전 재입력 요청
     - 메시지: "입력된 버전({입력버전})이 현재 버전({현재버전}) 이하입니다"
     - 선택지: 현재 버전의 patch/minor/major 각각 +1 한 버전
   - 재입력된 버전으로 이후 단계 진행

3. **로컬 상태 확인**
   - `git status --porcelain`으로 uncommitted 변경사항 확인
   - 변경사항이 있으면 경고 출력 후 종료

4. **기본 브랜치 확인**
   - current-branch가 default-branch가 아니면 경고 출력 후 종료

5. **Draft 릴리즈 존재 확인**
   - `gh release list --repo {repo} --limit 5`로 draft 릴리즈 존재 여부 확인
   - draft 릴리즈가 없으면 에러 출력 후 종료

6. **release 브랜치 존재 확인**
   - `--skip-sync` 인자가 있으면 이 단계 건너뛰기
   - `git ls-remote --heads origin release`로 원격 release 브랜치 확인
   - release 브랜치가 없으면 사용자에게 질문:
     - "release 브랜치가 없습니다. 어떻게 진행할까요?"
     - 선택지: "release 브랜치 생성 후 진행" / "브랜치 동기화 없이 진행"
   - 사용자가 "release 브랜치 생성" 선택 시 `git push origin {default-branch}:release`로 생성

### 버전 업데이트 및 변경 내역 작성

7. **Linear 이슈 및 브랜치 생성**
   - `/start-issue` 스킬 호출
   - 이슈 제목: `[compose] {version} 배포`
   - 이슈 설명: 작성하지 않음
   - 인자
    - labels: Deploy

8. **버전 파일 변경**
   - `pyproject.toml`의 `version` 필드 업데이트 (`v` 접두사 제거)

9. **변경 내역 작성** - `CHANGELOG.md`
   - `gh release view`로 draft 릴리즈 본문 조회
   - `## {version} ({YYYY-MM-DD})` 섹션을 기존 최상단 버전 위에 추가
   - 작성 원칙:
     - 패키지 사용자에게 영향 있는 변경만 포함
     - 내부 리팩터링, CI/CD, 스크립트, 문서 변경은 제외
     - PR 제목을 그대로 옮기지 않고 사용자 관점으로 재작성
     - API 변경 시 변경 후 API를 안내

10. **변경 내역 사용자 확인**
    - 작성된 changelog 내용을 사용자에게 보여주고 확인 요청
    - 수정 요청이 있으면 반영 후 다시 확인
    - 승인 후 다음 단계로 진행

11. **변경사항 커밋**
    - 커밋 메시지: `u: 프로젝트 버전을 {version}으로 업데이트`

### PR 생성 및 머지

12. **PR 생성**
    - `/submit-pr` 스킬 호출
    - 목적 섹션에 `{version} 배포` 작성

13. **PR 머지**
    - `/finish-pr` 스킬 호출
    - 인자: `--admin --wait --done`

### 릴리즈 준비

14. **Release Drafter 워크플로 완료 대기**
    - `gh run list --repo {repo} --workflow=release-drafter.yml --limit 1`로 최근 실행 확인
    - 상태가 `in_progress`인 경우 `gh run watch --repo {repo}`로 완료 대기
    - 실패한 경우 경고 출력 후 사용자 확인 요청

15. **Draft 릴리즈 노트 검증 및 누락 PR 추가**
    - `gh release list --repo {repo}`로 직전 릴리즈(draft가 아닌) 태그와 배포 일시 확인
    - `gh pr list --repo {repo} --state merged --search "merged:>{직전릴리즈일시}" --json number,title,labels,author`로 머지된 PR 목록 조회
    - `gh release view --repo {repo} {draft태그} --json body`로 현재 draft 릴리즈 본문 확인
    - 각 PR 번호(`#123`)가 draft 본문에 포함되어 있는지 검증
    - 누락된 PR이 있으면:
      - label → 섹션 매핑:
        - `feature`, `enhancement` → Features
        - `bug`, `fix` → Bug Fixes
        - `docs`, `documentation` → Documentation
        - 기타 → Other Changes
      - 형식: `- {PR제목} by @{author} in #{PR번호}`
      - `gh release edit --repo {repo} {draft태그} --notes "{수정된본문}"`으로 업데이트
    - 추가된 PR 목록 출력

### 릴리즈 배포

16. **Draft 릴리즈 배포**
    - draft 릴리즈의 태그가 입력된 버전과 다르면 `gh release edit --repo {repo}`로 태그/제목 수정
    - `gh release edit --repo {repo} {version} --draft=false`로 릴리즈 배포
    - 릴리즈 URL 출력

### 브랜치 동기화 (release 브랜치가 있는 경우에만)

`--skip-sync` 인자가 있거나 사용자가 "브랜치 동기화 없이 진행"을 선택한 경우 이 섹션 전체 건너뛰기.

17. **release 브랜치에 main 머지**
    - `git fetch origin`
    - `git switch release`
    - `git merge origin/{default-branch} --no-edit`
    - 충돌 발생 시:
      - 현재 상태 출력
      - `git merge --abort` 명령어 안내
      - 수동 해결 안내 후 중단

18. **release 브랜치 푸시**
    - `git push origin release`

19. **기본 브랜치로 복귀**
    - `git switch {default-branch}`
    - `git pull origin {default-branch}`

## 완료 메시지

- 버전 업데이트 PR URL
- 배포된 릴리즈 URL
- release 브랜치 동기화 결과 (실행됨/건너뜀)

## 주의사항

- 현재 브랜치가 기본 브랜치(main/master)여야 함
- Draft 릴리즈가 존재해야 함
- 브랜치 동기화 시 main과 release 간 충돌이 없어야 함
- 로컬에 uncommitted 변경사항이 없어야 함