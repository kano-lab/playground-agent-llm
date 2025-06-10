# playground-agent-llm

複数エージェント対話のLLMを用いたサンプルエージェントです。

## 環境構築

> [!IMPORTANT]
> Python 3.11以上が必要です。

```bash
git clone https://github.com/nharu-0630/playground-agent-llm.git
cd playground-agent-llm
cp config/config.yml.example config/config.yml
cp config/.env.example config/.env
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## その他

実行方法や設定などその他については[aiwolf-nlp-agent](https://github.com/aiwolfdial/aiwolf-nlp-agent)をご確認ください。
