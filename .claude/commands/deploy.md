---
allowed-tools: Bash(git:*), Bash(gh:*), mcp__linear__*
description: compose 패키지 배포 워크플로우 실행
argument-hint: <version> (예: 1.33.0)
---

# compose 배포 워크플로우

버전 $ARGUMENTS를 배포합니다.

## 실행 단계

1. **Linear 이슈 생성**
   - team: 내부제품
   - title: `[compose] v$ARGUMENTS 배포`
   - assignee: me
   - priority: 3 (Medium)
   - labels: Deploy
2. **브랜치 생성**: Linear 이슈의 gitBranchName으로 브랜치 생성
3. **버전 업그레이드**: pyproject.toml의 version을 $ARGUMENTS로 변경
4. **커밋**: `u: v$ARGUMENTS 배포` 형식으로 커밋
5. **PR 생성**: 템플릿 형식으로 PR 생성 (Deploy 라벨 추가)

## PR 생성 시 참고사항

- `.github/PULL_REQUEST_TEMPLATE.md` 형식을 따름
- 목적 섹션에 `v$ARGUMENTS 배포` 작성
- **반드시 `Deploy` 라벨을 추가해야 함** (gh pr create --label Deploy)

## 자동화 흐름

PR이 머지되면 `deploy-release.yml` 워크플로가 자동으로:
1. PR 제목에서 버전 추출
2. GitHub Release 생성 (태그 포함)
3. PyPI 배포 트리거 (publish.yml)