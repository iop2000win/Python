# ------------------------------------------------------------
# Categorical
# ------------------------------------------------------------
sample_df = pd.DataFrame([
                            ['all', 'F', '07-12'],
                            ['all', 'F', '13-18'],
                            ['all', 'F', '19-24'],
                            ['all', 'F', '25-29'],
                            ['all', 'F', '30-34'],
                            ['all', 'F', '35-39'],
                            ['all', 'F', '40-44'],
                            ['all', 'F', '45-49'],
                            ['all', 'F', '50-59'],
                            ['all', 'F', '60-69'],
                            ['all', 'F', '70+'],
                            ['all', 'F', '<07'],
                            ['all', 'M', '07-12'],
                            ['all', 'M', '13-18'],
                            ['all', 'M', '19-24'],
                            ['all', 'M', '25-29'],
                            ['all', 'M', '30-34'],
                            ['all', 'M', '35-39'],
                            ['all', 'M', '40-44'],
                            ['all', 'M', '45-49'],
                            ['all', 'M', '50-59'],
                            ['all', 'M', '60-69'],
                            ['all', 'M', '70+'],
                            ['all', 'M', '<07'],
                            ['all', 'O', 'OTHER']
                        ],
                        columns = ['retailer', 'gender_code', 'birth_code'])

'''
단순 정렬이 아니라, 내가 원하는 순서대로 정렬 순서를 지정해주고 싶을 때, Categorical 데이터 타입을 활용한다.
'''
# 단순 정렬
display(sample_df.sort_values(['birth_code']))

# 카테고리 정렬 - '<07'이 '07-12'보다 앞으로 오도록
cate_sort = ['<07', '07-12', '13-18', '19-24', '25-29', '30-34', '35-39',
             '40-44', '45-49', '50-59', '60-69', '70+', 'OTHER']

sample_df['birth_code'] = pd.Categorical(sample_df['birth_code'], categories = cate_sort, ordered = True)
display(sample_df.sort_values(['birth_code']))


# ------------------------------------------------------------
# to_excel
# ------------------------------------------------------------

df1 = pd.DataFrame()
df2 = pd.DataFrame()

output_path = './data/output.xlsx'

with pd.ExcelWriter(path) as writer:
    df1.to_excel(writer, sheet_name = 'sheet1', encoding = 'CP949', index = False)
    df2.to_excel(writer, sheet_name = 'sheet2', encoding = 'CP949', index = False)


# ------------------------------------------------------------
# dropna(subset = '', axis = , how = , inplace = )
# NULL값이 있는 데이터를 삭제하고 싶을 때 사용하는 메서드
# ------------------------------------------------------------
data = {
        'student_id': [1, 1, 1, 2, 2, 2, 13, 13, 13, 6, 6, 6],
        'student_name': ['Alice', 'Alice', 'Alice', None, None, None, 'John', 'John', 'John', 'Alex', 'Alex', 'Alex'],
        'subject_name': [None, 'Physics', 'Programming', None, 'Physics', 'Programming', None, 'Physics', 'Programming', None, 'Physics', 'Programming'],
        'attended_time': [3.0, 2.0, 1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0]
}

df = pd.DataFrame(data)

# null값이 하나라도 있는 row는 모두 삭제
df.dropna(axis = 0) # axis = 'rows'

# null값이 포함되어 있는 column 모두 삭제
df.dropna(axis = 1) # axis = 'columns'

# how변수를 통해 'any', 'all' 선택 가능
# any: null 값을 하나라도 포함하면 drop
# all: 해당 row/column 값이 전부다 null이어야 drop
df.dropna(axis = 0, how = 'any')

# 특정 컬럼에 대해서 null 값을 포함한 데이터를 삭제
df.dropna(subset = 'column_name')

# inplace 변수 사용 가능
df.dropna(subset = 'column_name', inplace = True)


# ------------------------------------------------------------
# melt() 메서드
# pivot의 반대 개념으로 wide data셋을 long data셋으로 바꾸는 기능
# 인덱스로 내릴 컬럼과 값으로 가져갈 컬럼을 잘 결정해야한다.
# ------------------------------------------------------------
df = pd.DataFrame({
                    'student': ['Alice', 'Bob'],
                    'Math': [90, 80],
                    'English': [85, 75]
                })

print(df)

pd.melt(
        df,
        id_vars = ['student'], # 컬럼으로 그대로 유지하고 싶은 값

        value_vars = ['Math', 'English'],
        # 컬럼 -> 로우로 변경하고 싶은 값으로 여러 개의 값을 리스트로 전달할 경우, 해당 값들이 하나의 컬럼 값으로 들어간다.
        # (왜 value_vars라고 할까? 해당 변수(variables)에 있는 값들이 melting 후에 값(value)으로 치환된다.)
        # 즉, 현재는 컬럼에 [수학 | 영어]이렇게 구성되어 있는데,
        # 이 두 컬럼을 [과목]이라는 하나의 컬럼으로 묶는 개념이다.
        # value_vars를 통해 하나로 묶이는 데이터의 컬럼명은 기본적으로 'variable' -> var_name
        # 해당 데이터가 가지고 있던 값은 'value'라는 컬럼명으로 표기 -> value_name
)

pd.melt(
        df,
        id_vars = ['student'],
        
        value_vars = ['Math', 'English'],
        var_name = 'Subject',
        value_name = 'Score'
)


# id_vars를 여러개 설정하는 것도 가능하다.
df = pd.DataFrame({
                    'year': [2020, 2021],
                    'region': ['North', 'South'],
                    'sales_q1': [100, 200],
                    'sales_q2': [150, 250]
                })
print(df)

df.melt(id_vars = ['year', 'region'],
        
        value_vars = ['sales_q1', 'sales_q2'],
        # sales_q1, sales_2 컬럼에 있는 값들이 value가 되고, 두 값은 변수 컬럼 아래의 값으로 melting
        var_name = 'quarter',
        value_name = 'sales'
)


# 다중 인덱스
df = pd.DataFrame({
                    'student_id': [1, 2],
                    'name': ['Alice', 'Bob'],
                    'midterm_math': [90, 85],
                    'midterm_english': [88, 80],
                    'final_math': [95, 82],
                    'final_english': [89, 78]
                })
print(df)

df_melted = df.melt(id_vars = ['student_id', 'name'],
                    # value_vars = ['midterm_math', 'midterm_english', 'final_math', 'final_english'],
                    # 변수 선언을 안해주면, 남은 컬럼 전체가 대상
                    var_name = 'exam_subject',
                    value_name = 'score')

df_melted[['exam', 'subejct']] = df_melted['exam_subject'].str.split('_', expand = True)
print(df_melted)


# ------------------------------------------------------------
# string 데이터 타입에 활용하는 판다스 시리즈 메서드
# - startswith() / endswith()
# - capitalize()
# - title()
# - swapcase()
# ------------------------------------------------------------
cities_df = pd.DataFrame({'city': ['moscow', 'Madrid', 'miami', 'berlin', 'Munich', 'seoul']})
print(cities_df)

print(cities_df['city'])
print(cities_df['city'].str.capitalize())
print(cities_df['city'].str.title())
print(cities_df['city'].str.swapcase())

cities_df_ = cities_df.loc[cities_df['city'].str.capitalize().str.startswith('M')]
print(cities_df_)


# ------------------------------------------------------------
# assign - pandas에서 새로운 컬럼을 할당하는 방법
# ------------------------------------------------------------
'''
assign을 통해 새로운 컬럼을 할당하는 방식과
df['new_column'] = 값 방식으로 새로운 컬럼을 할당하는 방식 2개가 존재 (insert도 존재)
기본적으로 새로운 컬럼을 할당하는 것은 동일

But,
- df['new_column'] : 직접 할당 >>> df 자체에 바로 적용되어 변환된다.
- df.assign(new_column) : 함수형 할당 >>> return으로 새로운 df를 반환.
실행 후에도 df 자체가 바뀌진 않는다.
- df['new_column'] 방식이 직관적. 간단한 컬럼 추가 작업은 해당 방식을 써도 상관없다.
- assign을 활용하면 체이닝을 하기가 편하기 때문에,
새로운 컬럼을 추가하면서 여러 조작을 한 번에 끝내려고 할 때는 assign을 활용한다.
'''
df = pd.DataFrame({
    'student': ['Alice', 'Bob', 'Charlie', 'David', 'Eva'],
    'class': ['A', 'A', 'B', 'B', 'A'],
    'math': [95, 82, 70, 60, 100],
    'english': [88, 75, 65, 70, 95],
})

# df['col'] 케이스
# df에 바로 적용되어 total 컬럼이 추가 되었다.
df_col = df.copy()
df_col['total'] = df_col['math'] + df_col['english']
print(df_col)

# df.assign 케이스
# assign을 통해 컬럼을 만들었지만 df에 적용되지 않았다.
df_asg = df.copy()
df_asg.assign(total = df_asg['math'] + df_asg['english'])
print(df_asg)

# 여러 컬러을 추가하려고 할 때
# df['col'] 케이스의 경우 각 컬럼별로 코드를 작성해야한다.
df_col['total'] = df_col['math'] + df_col['english']
df_col['mean'] = df[['math', 'english']].mean(axis = 1)

# 반면 assign을 활용할 경우, 여러 개의 컬럼을 한 번에 작성할 수 있다.
df_asg = df_asg.assign(total = df_asg['math'] + df_asg['english'],
                       mean = df_asg[['math', 'english']].mean(axis = 1))

# 체이닝 활용
result_df = (
                df.assign(total = df['math'] + df['english'],
                          mean = df[['math', 'english']].mean(axis = 1),
                          # 앞에서 만든 컬럼을 바로 활용하고 싶다면?
                        total_mean_sum = lambda x: x['total'] + x['mean'])
                    .query('mean >= 80') # query 메서드도 활용도가 매우 높다!
                    .groupby('class')
                    .agg(toal_sum = ('total', 'sum'),
                         mean_sum = ('mean', 'sum')
                        )
            )


# ------------------------------------------------------------
# groupby(['col_name'], as_index = True, dropna = True)
# groupby().nth()
# groupby().agg(col_name = ('target_col', lambda x: x))
# ------------------------------------------------------------
'''
groupby 메서드에 기본적으로 사용되는 파라미터에 대해서 알고가자.
as_index 값과 dropna 값은 default로 True로 돼있는데, 목적에 따라 False로 활용이 가능하다.
또한 agg 메서드 적용시에 함수 값으로 lambda 표현식도 적용이 가능하다.
'''
# dropna = True or False
# 그룹 키에 대해서 NULL 값을 어떻게 처리할 것인지 결정
# dropna = True >>> NULL 값 제외
# dropna = False >>> NULL 그룹 생성
df = pd.DataFrame({
                    'group': ['A', 'A', 'B', 'B', None, None],
                    'value': [1,   None, 3, None, 5,    None]
                })

df_dropna_true = df.groupby('group', dropna = True).size()
df_dropna_false = df.groupby('group', dropna = False).size()
'''
df_dropna_true
A    2
B    2
dtype: int64

df_dropna_false
A      2
B      2
NaN    2
dtype: int64
'''

# as_index - False값으로 주면 그룹 키가 인덱스로 되지 않고 컬럼 값으로 들어간다.

# agg 메서드에 lambda 표현식 적용 가능
df.groupby('group', as_index = False).agg(value_sum = ('value', lambda x: x.sum()))
'''
as_index = True
       value_cnt
group           
A            1.0
B            3.0

as_index = False
  group  value_cnt
0     A        1.0
1     B        3.0
'''

# groupby().nth() - 그룹에서 특정 위치(인덱스 위치)에 있는 행을 추출 (0 ~ -1)
'''
중복을 고려하지 않기 때문에, 동일한 값이 있을 경우를 고려해야한다. 단순히 rownum을 매기는 것
리스트 형식, 슬라이스 활용 가능
groupby().nth([0, 1, 2])
groupby().nth(slice(start, stop, step))
'''
df = pd.DataFrame({
                    'category': ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C'],
                    'value1': [10, 20, 30, 40, 50, 60, 70, 80],
                    'value2': [100, 200, 300, 400, 500, 600, 700, 800],
                    'rank':   [  1,   2,   3,   1,   2,   3,   1,   2]
                })

df.groupby('category').nth(1)
df.groupby('category').nth([0, 1, 2])
df.groupby('category').nth(slice(0, 6, 2))


# ------------------------------------------------------------
# df.mode(dropna = True) - 최빈값 찾아주는 메서드(null값 집계 여부)
# ------------------------------------------------------------
'''
최빈값을 찾아주는 메서드로 데이터 프레임과 시리즈에 모두 사용 가능하다.
데이터 프레임에 사용할 경우 최빈값을 찾는 기준이 되는 축을 axis = 0(열방향)/1(행방향) 값을 통해 지정해줘야한다.
(시리즈 타입의 경우 축 방향을 설정해주는 기능이 없다. 필요 없으므로)
dropna 파라미터의 경우 Null 값을 계산에 포함할지 여부를 결정하는 것으로 default = True 이다.
'''
df = pd.DataFrame({
                    'col1': [1, 2, 2, 3, np.nan, 2],
                    'col2': ['apple', 'apple', None, None, 'banana', None]
                })

df.mode(axis = 0)
df.mode(axis = 0, dropna = False)

df['col2'].mode()
df['col2'].mode(dropna = False)

# 최빈값이 n개인 경우 - 모든 최빈값을 나열해서 보여준다.
df_tie = pd.DataFrame({
                        'colA': [10, 10, 20, 20],
                        'colB': [1, 2, 3, 4]
                    })

df_tie.mode(axis = 0)
df_tie.mode(axis = 1)
'''
   colA  colB
0  10.0     1
1  20.0     2
2   NaN     3
3   NaN     4

   0   1
0  1  10
1  2  10
2  3  20
3  4  20
'''


# ------------------------------------------------------------
# pd.merge(left = left_df, right = right_df, how = 'cross') - 크로스 조인 기능 제공
# ------------------------------------------------------------
df1 = pd.DataFrame({
                    'key1': ['A', 'B']
                })
df2 = pd.DataFrame({
                    'key2': [1, 2, 3]
                })

df_cross = pd.merge(df1, df2, how = 'cross')
'''
  key1  key2
0    A     1
1    A     2
2    A     3
3    B     1
4    B     2
5    B     3
'''


# ------------------------------------------------------------
# df.to_dict(orient = '')
# ------------------------------------------------------------
'''
dict : {열 : {행 : 값, 행 : 값}, 열 : {행 : 값, 행 : 값}
list : {열 : [ 값 ], 열 : [ 값 ] }
series : {열 : Series, 열 : Series}
split : { index : [ 행, 행 ], columns : [ 열, 열 ], data : [ 값, 값 ] }
records : [ { 열 : 값 , 열 : 값 }, { 열 : 값, 열 : 값 } ]
index : { 행 : {열 : 값, 열 : 값}, 행 : {열 : 값, 열 : 값} }

orient 변수에 어떤 값을 주냐에 따라 데이터 프레임을 딕셔너리 형태로 변환하는 포맷이 달라진다.
여러가지 형태가 주어지지만, 개인적인 경험으로 많이 사용하는 형태에 대해서만 집중적으로 살펴보자.
데이터 프레임을 딕셔너리 형태로 바꾸려고 했던 경우는
인덱스 별로 컬럼 값을 조회하기 위한 경우가 많았다.
컬럼별로 데이터를 조회하거나, 컬럼과 인덱스 모두를 통해 데이터를 조회하는 경우는
데이터 프레임을 그대로 다루는 것이 더 편한 경우가 많았던 것 같다.

- orient = 'records' : 인덱스 별로 컬럼:값 을 조회
- orient = 'list' : 컬럼 별로 값을 리스트 형태로 조회
- orient = 'index' : 인덱스 별로 컬럼:값으로 조회
'''
data = {
    'A': [1, 2, 3],
    'B': [4, 5, 6],
    'C': [7, 8, 9]
}
df = pd.DataFrame(data)
print(df)

print(df.to_dict(orient = 'record'))
print(df.to_dict(orient = 'list'))
print(df.to_dict(orient = 'index'))
'''
   A  B  C
0  1  4  7
1  2  5  8
2  3  6  9

# records
[{'A': 1, 'B': 4, 'C': 7}, {'A': 2, 'B': 5, 'C': 8}, {'A': 3, 'B': 6, 'C': 9}]

# list
{'A': [1, 2, 3], 'B': [4, 5, 6], 'C': [7, 8, 9]}

# index
{0: {'A': 1, 'B': 4, 'C': 7},
 1: {'A': 2, 'B': 5, 'C': 8},
 2: {'A': 3, 'B': 6, 'C': 9}}
'''


# ------------------------------------------------------------
# df.index.levels
# df.index.names
# df.index.get_level_values(level)
# df.reset_index(level = )
# df.sort_index(level = )
# df.swaplevel(index1, index2)
# df.drop_level()
# ------------------------------------------------------------
'''
df에서 멀티 인덱스를 다룰 때 사용하는 개념
여러 층의 인덱스에 대해서 내가 원하는 층에 접근하여 데이터를 다루기 위한 기능
'''
index = pd.MultiIndex.from_tuples([('A', 1), ('A', 2), ('B', 1), ('B', 2)], names=['letter', 'number'])
df = pd.DataFrame({'value': [10, 20, 30, 40]}, index=index)

print(df)
'''
               value
letter number       
A      1          10
       2          20
B      1          30
       2          40
'''

print(df.index.levels)
print(df.index.names)
print(df.index.get_level_values(0))
print(df.index.get_level_values('letter'))
print(df.swaplevel('letter', 'number').sort_index(level = 'number'))
# print(df.swaplevel(0, 1).sort_index(level = 'number'))
'''
[['A', 'B'], [1, 2]]

['letter', 'number']

# get_level_values
Index(['A', 'A', 'B', 'B'], dtype='object', name='letter')
Index(['A', 'A', 'B', 'B'], dtype='object', name='letter')

# swaplevel
               value
number letter       
1      A          10
       B          30
2      A          20
       B          40
'''