# KouTube - セキュリティ学習用動画共有サイト

## プロジェクト概要
このプロジェクトは、仮想のWebシステムをPC内に構築し、講義内に学んだ知識でセキュリティ脆弱性のハッキングデモを行うことを目的としたプロジェクト実習用プロジェクトです。動画共有サイトシステムを構築しています。

## 使用技術
- **言語**: Python CGI
- **データベース**: MySQL
- **Webサーバー**: Apache

## 主な機能
- ユーザー登録・ログイン機能
- 動画アップロード・削除機能
- セッション管理機能
- 動画一覧表示機能

## セットアップ手順

### 1. Apache設定
```bash
# CGI設定ファイルの編集
sudo nano /etc/apache2/conf-available/cgi-enabled.conf

# 以下の内容を追加
<Directory /var/www/html/project>
    Options +ExecCGI +FollowSymLinks
    AllowOverride All
    AddHandler .cgi .pl
    Require all granted
</Directory>

# プロジェクトディレクトリの作成とシンボリックリンク
sudo mkdir /var/www/html/project
sudo ln -s /home/ユーザー名/projects/projitu_1 /var/www/html/project/

# Apache再起動
sudo systemctl restart apache2
```

### 2. データベース設定
MySQLでKouTubeデータベースを作成し、[MySQL.txt](setups/MySQL.txt)に記載されているテーブル構造を実行してください。

### 3. 動画保存ディレクトリ
```bash
# 動画保存用ディレクトリの作成
sudo mkdir -p /var/www/html/project/projitu_1/videos
sudo chmod 756 /var/www/html/project/projitu_1/videos
```

## ファイル構成
```
projitu_1/
├── cgi/
│   ├── login.cgi          # ログイン機能
│   ├── register.cgi       # ユーザー登録機能
│   ├── upload.cgi         # 動画アップロード機能
│   └── test.cgi          # テスト用CGI
├── videos/               # 動画ファイル保存ディレクトリ
├── MySQL.txt            # データベース設計書
├── command.txt          # セットアップコマンド
└── ReadME              # このファイル
```

## 脆弱性について（学習目的）
⚠️ **注意: このシステムは意図的にセキュリティ脆弱性を含んでいます。教育目的のみで使用し、本番環境では絶対に使用しないでください。**

### 実装されている脆弱性
1. **SQLインジェクション攻撃**
   - [login.cgi](cgi/login.cgi)のユーザー認証部分
   - [upload.cgi](cgi/upload.cgi)のセッション確認部分
   - [register.cgi](cgi/register.cgi)のユーザー登録部分

2. **クロス・サイト・スクリプティング（XSS）攻撃**
   - 入力値のサニタイズが不十分な箇所
   - HTMLエスケープ処理の不備

### 学習ポイント
- SQLインジェクション攻撃の仕組みと対策
- XSS攻撃の種類と防御方法
- セッション管理のセキュリティ
- 入力値検証の重要性

## アクセス方法
ブラウザで以下のURLにアクセス：
- テストページ: http://localhost/project/projitu_1/cgi/test.cgi
- ユーザー登録: http://localhost/project/projitu_1/cgi/register.cgi
- ログイン: http://localhost/project/projitu_1/cgi/login.cgi
- 動画アップロード: http://localhost/project/projitu_1/cgi/upload.cgi