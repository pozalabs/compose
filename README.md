# compose

Backend Components used in POZAlabs 

## MongoDB Query DSL

### 개념

- MongoDB의 쿼리 연산자를 선언형으로 사용할 수 있습니다.
- 모든 연산자는 `Operator`를 상속하며 `expression` 메서드를 구현합니다.
  - `expression` 메서드는 실제 MongoDB가 인식할 수 있는 형태의 쿼리 (Python dict/list) 표현식을 리턴합니다.
- 연산자는 Operator, Stage, Pipeline 세 가지 종류로 구분됩니다. 모든 연산자는 Operator입니다.
  - Operator: MongoDB의 쿼리 연산자를 선언형으로 사용할 수 있습니다.
  - Stage: MongoDB의 aggregation pipeline stage를 선언형으로 사용할 수 있습니다.
  - Pipeline: MongoDB의 aggregation pipeline을 선언형으로 사용할 수 있습니다.
- 연산자 이름은 MongoDB의 연산자 이름을 기본으로 사용하며, 구현 편의성에 따라 일부 이름을 확장하기도 합니다.
  - `$eq`: `Eq`
  - `$lookup`: `SubqueryLookup`, `MatchLookup`

### 사용법

#### 기본 연산

python
```python
from compose.query.mongo import op

op.And(
    op.Eq(field="field", value="value"),
    op.Gt(field="field", value=1),
).expression()
```

mongodb
```json
{
  "$and": [
    {
      "field": {
        "$eq": "value"
      }
    },
    {
      "field": {
        "$gt": 1
      }
    }
  ]
}
```
