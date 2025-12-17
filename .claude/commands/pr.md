---
allowed-tools: Bash(git:*), Bash(gh:*)
description: 현재 브랜치의 변경 사항으로 PR 생성
---

# PR 생성 워크플로우

현재 브랜치의 변경 사항을 분석하여 PR을 생성합니다.

## 실행 단계

1. **변경 사항 분석**
   - `git log main..HEAD`로 현재 브랜치의 커밋 확인
   - `git diff main...HEAD --stat`로 변경된 파일 확인
   - 대화 내역에서 작업 목적과 내용 파악

2. **브랜치 푸시**
   - `git push -u origin {현재브랜치명}`

3. **PR 생성**
   - `gh pr create`로 PR 생성
   - assignee: @me

## PR 제목 형식

- `{이슈번호}: [compose] 작업 내용 요약`
- 예: `IP-6824: [compose] FastAPIMessageConsumerRunner run/shutdown 메서드 분리`

## PR 본문 형식

`.github/PULL_REQUEST_TEMPLATE.md` 형식을 따름:

```markdown
## 목적
- 작업이 필요한 이유

## 변경 사항
- 주요 변경사항 목록
```