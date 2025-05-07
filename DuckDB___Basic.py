import duckdb as ddb

# 기본적인 사용법
# 커넥트 생성, 커넥트를 기반으로 쿼리문 작성
# 파일 경로 지정 X >>> 메모리 상에 테이블 생성 (':memory:')
# () == (':memory:') ':memory:'의 경우 명시적으로 메모리를 사용하겠다는 선언
# 하지만 명시적 표현에 차이가 있을 뿐 둘은 동일하게 작동한다.
conn = ddb.connect()

# 파일 경로 지정 O >>> 해당 경로에 .db파일 생성
# 파일로 데이터를 관리할 수 있다. 휘발성이 아니다.
conn = ddb.connect('./sample.db')


# .db 파일을 읽고 조회하는 방법
# connection을 활용하여 해당 로컬 .db파일에 커넥트한 후
# 일반 쿼리문과 동일하게 작성하면 된다.
conn = ddb.connect('./sample.db')

conn.sql('select * from sample_table;') # sample.db에 있는 sample_table의 데이터 조회
# .db 파일 명을 명시해줄 필요는 없다.

# 그렇다면 해당 .db에 어떤 테이블들이 있는지, 테이블은 어떻게 구성되어 있는지 확인하는 방법은?
# sql과 동일하게 쿼리문을 통해 조회해야한다.
result = conn.sql("""
select	table_name
from	information_schema.tables
where	table_schema = 'main';
	""")
# 'main' 자리에 db명을 입력하면 된다.
print(result)


# 컬럼 정보 조회
result = conn.sql("""
select	column_name, data_type, is_nullable
from	information_schema.columns
where	table_name = ''
	""")
print(result)



# 커넥트 생성
'''
기본적으로 커넥트를 생성하고, 해당 커넥트에 쿼리문을 날리는 방식으로 작동한다.
일반적인 데이터 베이스의 커넥트와 동일하게 이해하면 된다.


read_parquet - 메모리 내의 가상 테이블로 변환하여 해당 데이터를 로드
세션 종료시에 해당 데이터는 휘발된다.
read한 결과를 변수에 담지 않을 경우에는 결과는 바로 휘발된다.
변수에 담으면 기본적으로 duckdb relation 형태로 저장된다.
(이 경우 parquet 파일의 경우 속도가 매우 빠르다.)

이를 dataframe으로 변환하여 조작


커넥션을 생성하는 것과 생성하지 않는 것의 차이는?

커넥션을 생성하지 않고, duckdb 라이브러리의 함수를 활용해서 데이터를 조회할 경우,
라이브러리 내부에서 자동으로 커넥션을 생성하여 데이터를 처리한다.

명시적으로 커넥션을 설정하고, 해당 커넥션의 메서드를 통해 데이터를 처리할 수도 있다.

자동 커넥션 생성을 활용할 경우, 사용자가 명시적으로 생성해줄 필요가 없으므로
편하게 작업을 진행할 수 있다.

명시적 커넥션을 설정할 경우, 내가 현재 어떤 커넥션에서 데이터를 처리하고 있는지를
명확하게 알 수 있으며, 커넥션 단위로 데이터를 작업하기에도 용이하다.
또한 커넥션을 클로즈 하면 관련 데이터 모두 내려가기 때문에 메모리 관리 측면에서도 유용한 점이 있다.
'''




# conn.sql / conn.execute / ddb.sql 차이는?
'''
둘 다 duckdb를 통해 쿼리문을 실행하는 방법이지만, 사용 방식과 목적에 차이가 존재

1. execute()
일반적으로 테이블 생성, 변경 등 데이터를 조정하는 작업을 할 때 사용
데이터를 조회할 때도 사용하지만, 이 경우 .sql을 통해 조회하는 것과 달리
duckdb relation 형태로 바로 데이터를 조회할 수 없고,
파이썬의 여러 데이터 타입 형태로 변환해서 결과를 받아볼 수 있다.
하지만 이렇게 할 경우, 대용량 데이터를 읽어드릴 때
소요시간이 오래 걸리고, 오버헤드가 발생할 수 있다

2. .sql()
sql 메서드를 사용하면 duckdb relation 객체를 직접 반환 받을 수 있다.
duckdb relation은 지연 평가(lazy evaluation) 방식으로 작동하는데,
이로 인해서 데이터를 조회하고, 집계하는데 있어서 매우 빠르고 효율적이다.
지연 평가 방식이란 데이터를 바로 메모리에 올리는 것이 아니라,
데이터에 대한 모든 연사 처리를 메모리에 올리기 전에 수행한 후,
최종 결과물만 메모리에 업로드하는 방식을 말한다.
이로 인해 불필요한 오버헤드나 메모리 낭비가 없게 된다.

3. 결론
데이터 정의 작업(테이블 생성, 데이터 삽입/수정/삭제)을 위한 쿼리문을 쓸 때는
execute 메서드를 사용
- create table
- insert into
- delete from
- update
- alter table

데이터 조회 및 집계 등을 위한 쿼리문을 쓸 때는 sql 메서드를 이용하여 지연 평가 방식을 활용할 것
polars처럼 체이닝을 이용하여 여러 연산을 연이어 적용할 수도 있다.
'''



ddb.sql('select 1 as sample_columns').show()
'''
┌────────────────┐
│ sample_columns │
│     int32      │
├────────────────┤
│              1 │
└────────────────┘

위와 같이 duckdb 라이브러리의 함수인 sql을 사용하여 쿼리문을 실행했을 경우,
내부적으로 자동으로 커넥션이 생성되고 해당 커넥션으로 쿼리문이 작동하게 된다.

show() 메서드는 pandas의 display와 마찬가지로 해당 결과를 출력해주는 기능이다.
'''

conn = ddb.connect() # ddb.connect(':memory:'), 입력 값으로 .db 경로를 지정해주면 .db 파일을 생성한다.
conn.sql('select 1 as conn_sample_columns')
'''
┌─────────────────────┐
│ conn_sample_columns │
│        int32        │
├─────────────────────┤
│                   1 │
└─────────────────────┘

connection을 만들고 해당 connection이 제공하는 메서드를 통해 쿼리문을 실행하는 방식
'''

# duckdb.read_parquet(sample.parquet) vs. duckdb.sql("select * from sample.parquet")
'''
두 방식 모두 동일하게 sample 파일을 duckdb relation 파일로 읽어오는 작업을 수행한다. 결과값도 동일.

그렇다면 무슨 차이가 있는가?
단순 파일 데이터 전체를 읽기 위함이 아니라, 데이터를 집계하거나 전처리를 포함한 작업을 진행한다고 했을 때,
차이점이 발생한다.

- read_parquet()
파일을 우선 그대로 다 읽어들인다. 파일을 다 읽어들여서 테이블로 형태로 취급하는 것.
즉, 집계를 하든, 전처리를 하든 1차적으로 전체 데이터를 다 읽고나서 후속 작업을 진행하는 식.

- .sql()
parquet 파일 자체를 하나의 테이블로 취급.
파일 조회 당시에 쿼리문을 작성하여, 파일을 읽어오기 전에 원하는 집계 및 전처리를 먼저 진행하고
해당 결과만 읽어올 수 있다.
'''