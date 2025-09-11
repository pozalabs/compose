# 의존성 그래프 기반 작업 파이프라인 설계

## 개요

순차적인 단계별 작업 처리 방식을 개선하여, 작업별 의존성에 따른 동적 파이프라인 실행으로 전체 처리 시간을 최적화하는 범용 설계입니다. 이 패턴은 ETL, 빌드 시스템, 데이터 파이프라인 등 다양한 영역에서 활용할 수 있습니다.

## 문제 정의

### 현재 구조 (순차 처리)

```python
executor.execute(stage1_jobs)    # 1단계: 모든 작업 완료 대기
executor.execute(stage2_jobs)    # 2단계: 모든 작업 완료 대기  
executor.execute(stage3_jobs)    # 3단계: 모든 작업 완료 대기
```

### 문제점
- 각 단계가 모두 완료되어야 다음 단계 시작
- 빠르게 완료된 작업도 느린 작업을 기다려야 함
- 전체 처리 시간 = 각 단계별 최대 작업 시간의 합

## 설계 목표

### 개선된 구조 (의존성 기반 파이프라인)
작업 완료 즉시 의존하는 다음 작업들을 실행

```
stage1_A → stage2_group1 → stage3_A1, stage3_A2
stage1_B →                → stage3_B1  
stage1_C → stage2_group2 → stage3_C1
```

**핵심 개념**: 개별 작업 단위의 의존성 관리로 파이프라인 병렬성 극대화

## 핵심 컴포넌트

### 1. DependencyJob

```python
from typing import Callable, Any
from dataclasses import dataclass

@dataclass
class DependencyJob:
    """의존성을 가진 작업 단위"""
    job_id: str                           # 고유 작업 식별자
    func: Callable[..., Any]              # 실행할 함수
    kwargs: dict[str, Any]                # 함수 인자
    dependencies: list[str] = None        # 선행 작업 ID 목록
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
```

### 2. DependencyGraphExecutor

```python
class DependencyGraphExecutor:
    """의존성 그래프 기반 동적 작업 스케줄러"""
    
    def __init__(self, max_workers: int):
        self.max_workers = max_workers
    
    def execute(self, jobs: list[DependencyJob]) -> dict[str, Any]:
        """의존성 그래프에 따라 작업들을 동적으로 실행"""
```

## 구현 알고리즘

### 핵심 로직
1. **그래프 구축**: 작업들의 의존성 관계를 매핑
2. **동적 스케줄링**: 의존성이 해결된 작업들을 실행 큐에 추가
3. **병렬 실행**: `concurrent.futures.ThreadPoolExecutor` 사용
4. **완료 감지**: `as_completed()`로 완료 순서대로 처리
5. **체인 반응**: 완료된 작업으로 인해 준비된 새 작업들을 즉시 스케줄

### 의존성 해결 로직
```python
# 작업 완료 시 의존성 체크
for job in jobs:
    if (job.job_id not in completed and 
        all(dep in completed for dep in job.dependencies)):
        ready_queue.put(job.job_id)  # 준비된 작업 큐에 추가
```

### 실행 메커니즘 상세

#### 메인 실행 루프
```python
while len(completed) < len(jobs):  # 모든 작업이 완료될 때까지 반복
    # 1. 작업 제출 단계
    while not ready_queue.empty() and len(active_futures) < self.max_workers:
        job_id = ready_queue.get()
        job = job_map[job_id]
        future = executor.submit(job.func, **job.kwargs)
        active_futures[future] = job_id
    
    # 2. 완료 감지 및 처리
    if active_futures:
        done_futures = concurrent.futures.as_completed(active_futures, timeout=0.1)
        for future in done_futures:
            job_id = active_futures.pop(future)
            completed[job_id] = future.result()
            
            # 3. 의존성 해결된 새 작업들 찾기
            for job in jobs:
                if (job.job_id not in completed and 
                    all(dep in completed for dep in job.dependencies)):
                    ready_queue.put(job.job_id)
```

#### as_completed() 동작 원리
- **논블로킹**: `timeout=0.1`로 짧은 시간만 대기
- **완료 순서**: 제출 순서가 아닌 **완료되는 순서대로** 반환
- **즉시 처리**: 하나라도 완료되면 바로 반환해서 의존성 체크 시작

## 사용 예제: 3단계 파이프라인

### 파이프라인 작업 정의
```python
def build_pipeline_jobs(items: list[str]) -> list[DependencyJob]:
    jobs = []
    
    # 1단계: 개별 입력 처리 (의존성 없음)
    for item in items:
        jobs.append(DependencyJob(
            job_id=f"stage1_{item}",
            func=stage1_function,
            kwargs={"item": item},
            dependencies=[]
        ))
    
    # 2단계: 그룹 단위 처리 (관련 1단계 완료 후)
    for group_id, group_items in group_items_by_criteria(items):
        stage2_job_id = f"stage2_{group_id}"
        dependencies = [f"stage1_{item}" for item in group_items]
        jobs.append(DependencyJob(
            job_id=stage2_job_id,
            func=stage2_function,
            kwargs={"items": group_items},
            dependencies=dependencies
        ))
    
    # 3단계: 개별 결과 처리 (2단계 완료 후)
    for group_id, group_items in group_items_by_criteria(items):
        stage2_job_id = f"stage2_{group_id}"
        for item in group_items:
            jobs.append(DependencyJob(
                job_id=f"stage3_{item}",
                func=stage3_function,
                kwargs={"item": item},
                dependencies=[stage2_job_id]
            ))
    
    return jobs

# 사용 예시
executor = DependencyGraphExecutor(max_workers=4)
jobs = build_pipeline_jobs(["data1", "data2", "data3"])
results = executor.execute(jobs)
```

### 실행 시나리오 예시
```
시작: stage1_A, stage1_B, stage1_C 병렬 실행 (의존성 없음)
0.5초 후: stage1_A 완료 → stage2_group1 의존성 체크 → 대기 (stage1_B 미완료)
1.0초 후: stage1_B 완료 → stage2_group1 의존성 완료 → 즉시 실행 시작
1.2초 후: stage2_group1 완료 → stage3_A1, stage3_A2 큐에 추가 → 즉시 병렬 실행
1.5초 후: stage1_C 완료 → stage2_group2 즉시 실행 시작
```

**효과**: 각 작업이 완료되는 즉시 다음 의존 작업들이 스케줄링되어 전체 처리 시간 단축

## 파일 구조

### 새로 추가할 파일
- `dependency_executor.py`: `DependencyJob`, `DependencyGraphExecutor` 구현

### 통합 방법
1. 기존 순차 처리 코드를 의존성 작업으로 변환
2. `DependencyGraphExecutor` 인스턴스 생성
3. 작업 의존성 그래프 정의 후 실행

## 기대 효과

1. **처리 시간 단축**: 단계별 완료 대기 → 작업별 완료 즉시 파이프라인 진행
2. **리소스 효율성**: CPU/메모리 사용률 향상 및 대기 시간 최소화
3. **확장성**: ETL, 빌드 시스템, 데이터 파이프라인 등 다양한 영역 적용 가능
4. **유지보수성**: 명확한 의존성 정의로 작업 흐름 가시성 향상
5. **장애 격리**: 개별 작업 실패가 무관한 다른 파이프라인에 영향 없음

## 호환성 고려사항

- **Python 표준**: `dataclass`와 `concurrent.futures` 사용으로 외부 의존성 최소화
- **기존 인터페이스**: 기존 함수 시그니처 변경 없이 래핑 가능
- **ThreadPoolExecutor**: 내부 구현체로 사용, 검증된 병렬 처리 방식 활용

## 구현 가이드

### 1. 의존성 그래프 검증
- 순환 의존성 탐지 로직 추가
- 잘못된 의존성 ID 참조 검증

### 2. 에러 처리
- 작업 실패 시 의존하는 작업들의 처리 방안
- 부분 실패 시 롤백 전략

### 3. 모니터링
- 작업별 실행 시간 측정
- 의존성 체인 시각화 (디버깅용)

### 4. 테스트
- 단위 테스트: 의존성 해결 로직
- 통합 테스트: 실제 파이프라인 실행
- 성능 테스트: 기존 방식 대비 처리 시간 비교

## 완전한 구현 예제

```python
import concurrent.futures
import queue
from typing import Callable, Any, Dict
from dataclasses import dataclass

@dataclass
class DependencyJob:
    job_id: str
    func: Callable[..., Any]
    kwargs: dict[str, Any]
    dependencies: list[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class DependencyGraphExecutor:
    def __init__(self, max_workers: int):
        self.max_workers = max_workers
    
    def execute(self, jobs: list[DependencyJob]) -> dict[str, Any]:
        job_map = {job.job_id: job for job in jobs}
        completed = {}
        ready_queue = queue.Queue()
        
        # 초기 준비된 작업들 (의존성 없음)
        for job in jobs:
            if not job.dependencies:
                ready_queue.put(job.job_id)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            active_futures = {}
            
            while len(completed) < len(jobs):
                # 준비된 작업들 제출
                while not ready_queue.empty() and len(active_futures) < self.max_workers:
                    job_id = ready_queue.get()
                    job = job_map[job_id]
                    future = executor.submit(job.func, **job.kwargs)
                    active_futures[future] = job_id
                
                # 완료된 작업 처리
                if active_futures:
                    try:
                        done_futures = concurrent.futures.as_completed(active_futures, timeout=0.1)
                        for future in done_futures:
                            job_id = active_futures.pop(future)
                            completed[job_id] = future.result()
                            
                            # 의존성 해결된 새 작업들 찾기
                            for job in jobs:
                                if (job.job_id not in completed and 
                                    job.job_id not in [active_futures[f] for f in active_futures] and
                                    all(dep in completed for dep in job.dependencies)):
                                    ready_queue.put(job.job_id)
                                    break
                    except concurrent.futures.TimeoutError:
                        continue
        
        return completed
```