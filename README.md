# aiwolf-nlp-agent

人狼知能コンテスト2024冬季 国内大会（自然言語部門） のサンプルエージェントです。

ローカル内での動作確認ならびに自己対戦するためのゲームサーバについては、[kano-lab/aiwolf-nlp-server](https://github.com/kano-lab/aiwolf-nlp-server) を参考にしてください。  
大会の詳細ならびに参加登録については、[AIWolfDial2024WinterJp](https://sites.google.com/view/aiwolfdial2024winterjp/) を参考にしてください。

大会参加者はエージェントを実装したうえで、ご自身の端末でエージェントを実行、大会運営が提供するゲームサーバに接続する必要があります。エージェントの実装については、実装言語を含め、制限はありません。  
自己対戦では、5体のエージェントをご自身の端末で実行し、大会運営が提供する自己対戦用のゲームサーバに接続しすることで、エージェント同士の対戦を行うことができます。

## 環境構築

> [!IMPORTANT]
> Python 3.11以上が必要です。

```
git clone https://github.com/kano-lab/aiwolf-nlp-agent.git
cd aiwolf-nlp-agent
python -m venv .venv
source .venv/bin/activate
pip install .
```

> [!NOTE]
> aiwolf-nlp-commonとは、役職や接続方式に関するプログラムが定義されているPythonパッケージです。  
> 詳細については、https://github.com/kano-lab/aiwolf-nlp-common をご覧ください。

## 実行方法

### 自己対戦

事前に、ローカル内にゲームサーバを立ち上げる必要があります。  
[kano-lab/aiwolf-nlp-server](https://github.com/kano-lab/aiwolf-nlp-server) を参考にしてください。

```
cp config/config.ini.example config/config.ini
cp config/log.ini.example config/log.ini
python src/main.py
```

## 設定 (config.ini)

### [websocket]

`url`: ゲームサーバのURLです。ローカル内のゲームサーバに接続する場合はデフォルト値で問題ありません。
`token`: ゲームサーバに接続するためのトークンです。大会運営から提供されるトークンを設定してください。
`auto_reconnect`: 対戦終了後に自動で再接続するかどうかの設定です。

### [agent]

`num`: 起動するエージェントの数です。自己対戦の場合はデフォルト値で問題ありません。  
`team`: エージェントのチーム名です。大会運営から提供されるチーム名を設定してください。

## ログの設定 (log.ini)

### [log]

`get_info`: ゲームサーバから取得したJsonをログに書き込むかどうかの設定です。  
`initialize`: Initializeリクエストの時にゲームサーバから取得したJsonをログに書き込むかどうかの設定です。  
`talk`: エージェントがゲームサーバに送信した`TALK`の内容ををログに書き込むかどうかの設定です。  
`vote`: エージェントがゲームサーバに送信した`VOTE`の内容ををログに書き込むかどうかの設定です。  
`divine`: エージェントがゲームサーバに送信した`DIVINE`の内容ををログに書き込むかどうかの設定です。  
`divine_result`: ゲームサーバから取得した占いの結果をログに書き込むかどうかの設定です。  
`attack`: エージェントがゲームサーバに送信した`ATTACK`の内容ををログに書き込むかどうかの設定です。  

### [path]

`output_dir`: エージェントのログを保存するパスの設定です。デフォルト値で問題ありません。
