# 第6回 解答

## 演習

<!-- [tool call] の行は、表示された行をそのまま貼り付けてください。終わらなかった STEP は、空欄のままでかまいません。 -->

- STEP 1 のツールの名前：glossary_search_glossary
- STEP 2 の [tool call]：[tool call]   glossary_search_glossary({'query': '3レベル'})
- STEP 3 の [tool call]：[tool call]   fetch_fetch({'url': 'https://modelcontextprotocol.io/'})
- STEP 4 の [tool call]：[tool call]   aws_aws___search_documentation({'search_phrase': 'Amazon S3 バージョニング 概要', 'topics': ['general']})

[tool call]   aws_aws___search_documentation({'topics': ['general'], 'search_phrase': 'Using versioning in S3 buckets'})
- 気づき・疑問：
 - 従来の関数呼び出しとMCP経由のツール呼び出しを比較し、MCPではサーバー側で公開したツールをエージェントが取得して利用できることを確認した。
  - ローカルのMCPサーバーと、HTTP経由で接続するAWSのリモートMCPサーバーの違いも理解できた。
  - 外部ツールの利用時には権限管理やエラーへの対応が重要だと感じた。


## 宿題

<!-- 基礎・実装・発展のどれか1つに取り組めば完了です。 -->

- 取り組んだレベル：基礎 / 実装 / 発展
- やったこと：
- 結果：
- 気づき・疑問：
