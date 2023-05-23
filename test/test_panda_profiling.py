import pandas as pd
import pandas_profiling

# 创建 DataFrame
data = {'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 35],
        'Salary': [50000, 60000, 70000]}
df = pd.DataFrame(data)

# 使用 pandas_profiling 生成 HTML 报告
report = df.profile_report()

# 将报告保存为 HTML 文件
report.to_file('report.html')
