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

```python
from compose.query.mongo import op

op.And(
    op.Eq(field="field", value="value"),
    op.Gt(field="numeric_field", value=1),
).expression()
```

```json
{
  "$and": [
    {
      "field": {
        "$eq": "value"
      }
    },
    {
      "numeric_field": {
        "$gt": 1
      }
    }
  ]
}
```

#### Aggregation

Aggregation 표현식은 Stage, Operator 조합해 표현하며, Stage 목록을 Pipeline에 입력하면 Aggregation 표현식을 얻을 수 있습니다.

Match, Sort

```python
from compose.query.mongo import op

op.Pipeline(
    op.Match.and_(
        op.Eq(field="field", value="value"),
        op.Gt(field="numeric_field", value=1),
    ),
    op.Sort(
        op.Sortby.asc("numeric_field"),
    ),
)
```

```json
[
  {
    "$match": {
      "$and": [
        {
          "field": {
            "$eq": "value"
          }
        },
        {
          "numeric_field": {
            "$gt": 1
          }
        }
      ]
    }
  },
  {
    "$sort": {
      "numeric_field": 1
    }
  }
]
```

Match Lookup

```python
from compose.query.mongo import op

op.Pipeline(
  op.MatchLookup(
    from_="from_collection",
    local_field="local_field",
    foreign_field="foreign_field",
    as_="as_field",
  ),
  op.Unwind("$as_field"),
)
```

```json
[
  {
    "$lookup": {
      "from": "from_collection",
      "localField": "local_field",
      "foreignField": "foreign_field",
      "as": "as_field"
    }
  },
  {
    "$unwind": {"patch": "$as_field"}
  }
]
```

Subquery Lookup

```python
from compose.query.mongo import op

op.Pipeline(
  op.SubqueryLookup(
    from_="from_collection",
    as_="as_field",
    pipeline=op.Pipeline(
      op.Match.and(
        op.Expr(op.Eq(field="field", value="value")),
      )
    )
  ),
  op.Unwind("$as_field"),
)
```

```js
[
  {
    "$lookup": {
      "from": "from_collection",
      "as": "as_field",
      "pipeline": [
        {
          "$match": {
            "$and": [
              {
                "$eq": ["field", "value"]
              }
            ]
          }
        }
      ]
    }
  },
  {
    "$unwind": {
      "patch": "$as_field"
    }
  }
]
```