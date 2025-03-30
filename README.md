# aiwolf-nlp-agent
人狼知能コンテスト（自然言語部門） のサンプルエージェントです。

<!-- START doctoc -->
<!-- END doctoc -->

## 次回大会について
最新情報は[aiwolfdial.github.io](https://aiwolfdial.github.io/aiwolf-nlp/)をご確認ください。

また、2025年度人工知能学会全国大会に向けた大会では下記が予定されています。

> [!IMPORTANT]
> - トークリクエストならびに囁きリクエストにおける発言の文字数制限の追加
> - 13人ゲームの追加
> - カスタムプレイヤー名とカスタムプロフィールの追加

### 13人-人狼
13人人狼で現在想定している役職は下記の通りです。
| 役職 | 陣営 | 人数 | 特殊能力 |
| ---- | ---- | ---- | ---- |
| 村人 | 村人 | 6 | なし |
| 占い師 | 村人 | 1 | 夜のターンに1名選択し、そのプレイヤーの陣営を知ることができる |
| 霊媒師 | 村人 | 1 | 投票によって追放されたプレイヤーの陣営を知ることができる |
| 騎士 | 村人 | 1 | 夜のターンに1名選択し、そのプレイヤーを人狼の襲撃から守ることができる |
| 人狼 | 人狼 | 3 | 夜のターンに1名選択し、そのプレイヤーを襲撃することでゲームから除外することができる |
| 狂人 | 人狼 | 1 | 人狼陣営の勝利が自身の勝利になる |

### 5人-人狼
| 役職 | 陣営 | 人数 | 特殊能力 |
| ---- | ---- | ---- | ---- |
| 村人 | 村人 | 2 | なし |
| 占い師 | 村人 | 1 | 夜のターンに1名選択し、そのプレイヤーの陣営を知ることができる |
| 人狼 | 人狼 | 1 | 夜のターンに1名選択し、そのプレイヤーを襲撃することでゲームから除外することができる |
| 狂人 | 人狼 | 1 | 人狼陣営の勝利が自身の勝利になる |

大会参加者はエージェントを実装したうえで、ご自身の端末でエージェントを実行、大会運営が提供するゲームサーバに接続する必要があります。エージェントの実装については、実装言語を含め、制限はありません。  
自己対戦では、5体のエージェントをご自身の端末で実行し、大会運営が提供する自己対戦用のゲームサーバに接続しすることで、エージェント同士の対戦を行うことができます。

ローカル内での動作確認ならびに自己対戦するためのゲームサーバについては、[aiwolfdial/aiwolf-nlp-server](https://github.com/aiwolfdial/aiwolf-nlp-server) を参考にしてください。

次回大会の詳細についてはしばらくお待ちください。

## 環境構築

> [!IMPORTANT]
> Python 3.11以上が必要です。

```bash
git clone https://github.com/aiwolfdial/aiwolf-nlp-agent.git
cd aiwolf-nlp-agent
python -m venv .venv
source .venv/bin/activate
pip install .
```

> [!NOTE]
> aiwolf-nlp-commonとは、役職や接続方式に関するプログラムが定義されているPythonパッケージです。  
> 詳細については、[aiwolfdial/aiwolf-nlp-common](https://github.com/aiwolfdial/aiwolf-nlp-common) をご覧ください。

## 実行方法

### 自己対戦

事前に、ローカル内にゲームサーバを立ち上げる必要があります。  
[aiwolfdial/aiwolf-nlp-server](https://github.com/aiwolfdial/aiwolf-nlp-server) を参考にしてください。

```bash
cp config/config.yml.example config/config.yml
python src/main.py
```

## 設定 (config.yml)

### web_socket

`url`: ゲームサーバのURLです。ローカル内のゲームサーバに接続する場合はデフォルト値で問題ありません。
`token`: ゲームサーバに接続するためのトークンです。大会運営から提供されるトークンを設定してください。
`auto_reconnect`: 対戦終了後に自動で再接続するかどうかの設定です。

### agent

`num`: 起動するエージェントの数です。自己対戦の場合はデフォルト値で問題ありません。  
`team`: エージェントのチーム名です。大会運営から提供されるチーム名を設定してください。

### log

`console_output`: コンソールにログを出力するかどうかの設定です。  
`file_output`: ファイルにログを出力するかどうかの設定です。  
`output_dir`: ログを保存するディレクトリのパスです。  
`level`: ログの出力レベルです。`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`のいずれかを設定してください。

#### log.requests

`name`, `initialize`, `daily_initialize`, `whisper`, `talk`, `daily_finish`, `divine`, `guard`, `vote`, `attack`, `finish`: 各リクエストのログを出力するかどうかの設定です。
