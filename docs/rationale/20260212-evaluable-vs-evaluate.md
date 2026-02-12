# Evaluable vs evaluate 사용 기준

## 맥락

- `Evaluable`은 dict/list를 재귀 탐색하여 중첩된 Operator를 모두 평가한다
- `evaluate`는 값이 Operator이면 `expression()`을 호출하고, 아니면 그대로 반환한다
- 반환 구조가 고정된 operator에서 `Evaluable`을 사용하면 불필요한 재귀 탐색이 발생한다

## 결정

operator의 `expression()` 구현 시, 반환값의 구조에 따라 선택한다.

### `evaluate` 사용: 구조가 고정된 경우

반환할 dict/list의 구조를 코드에서 직접 구성하고, 각 값의 위치를 알고 있을 때.

```python
# 각 값을 명시적으로 evaluate
def expression(self):
    return {"$split": [evaluate(self.expr), self.delimiter]}
```

해당 operator:
- `First`, `MergeObjects`, `AddToSet`, `Push`
- `ToString`, `ToBool`, `ToInt`
- `Split`, `RegexMatch`
- `SetIntersection`, `IndexOfArray`, `ArrayElemAt`
- `Expr`

### `Evaluable` 사용: 사용자 입력 구조를 그대로 전달하는 경우

사용자가 전달한 dict/list 내부에 Operator가 임의 위치에 중첩될 수 있을 때.

```python
# 사용자가 전달한 spec dict 내부에 Operator가 중첩될 수 있음
def expression(self):
    return {self.field: Evaluable(self.spec).expression()}
```

해당 operator:
- `Raw`: 사용자가 구성한 임의 dict을 받음 (e.g., `Raw({"$first": Filter(...)})`)
- `GeneralAggregationOperator`: expressions list에 Operator가 중첩 가능
- `Spec`, `Group`, `Project`: 사용자 정의 필드 매핑을 받음
- `Lookup` 계열: pipeline 등 중첩 구조 포함
- `Map`, `Filter`, `Reduce`, `SortArray`, `Cond`: 내부 expression에 Operator 중첩 가능

### 직접 반환: Operator가 포함될 수 없는 경우

모든 값이 primitive일 때는 `evaluate`도 불필요하다.

```python
# self.size는 int — 평가할 것이 없음
def expression(self):
    return {"$sample": {"size": self.size}}
```

## 판단 기준

- 반환할 dict의 각 값이 `self.xxx`로 특정되고, 타입이 `Operator | primitive`이면 → `evaluate`
- 반환할 dict/list가 사용자로부터 받은 구조를 그대로 포함하면 → `Evaluable`
- 모든 값이 primitive이면 → 직접 반환
