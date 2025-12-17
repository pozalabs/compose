---
allowed-tools: Bash(git:*), mcp__linear__*
description: 대화 내역 기반 Linear 이슈 생성 및 브랜치 생성
argument-hint: "[--priority <urgent|high|medium|low>] [--labels <label1,label2,...>]"
---

# Kickoff 워크플로우

대화 내역을 바탕으로 Linear 이슈를 생성하고 작업 브랜치를 만듭니다.

## 인자

- `--priority`: 이슈 우선순위 (기본값: medium)
  - urgent (1), high (2), medium (3), low (4)
- `--labels`: 이슈 라벨 (기본값: Feature)
  - 쉼표로 구분하여 여러 개 지정 가능

**입력된 인자**: $ARGUMENTS

## 실행 단계

1. **대화 내역 분석**
   - 지금까지의 대화에서 작업 목적과 내용을 파악
   - 이슈 제목과 설명 도출

2. **Linear 이슈 생성**
   - team: 내부제품
   - title: 대화 내역 기반으로 작성 (예: `[compose] 기능명`)
   - description: 작업 배경과 구현 내용 요약
   - assignee: me
   - priority: 인자로 전달된 값 또는 기본값 medium (3)
   - labels: 인자로 전달된 값 또는 기본값 Feature
   - estimate: 1

3. **브랜치 생성**
   - 생성된 이슈의 gitBranchName으로 새 브랜치 생성
   - `git switch -c {gitBranchName}`

## 이슈 제목 형식

- `[compose] 작업 내용 요약`
- 한국어로 간결하게 작성

## 이슈 설명 형식

```markdown
## 배경
- 작업이 필요한 이유

## 구현 내용
- 주요 변경사항 목록
```