# English Placement Test — Streamlit Pilot

A Streamlit app for piloting an English placement test. Questions load from `English Placement 1.5.csv`, one sub-question per page, with responses saved to DynamoDB when configured.

## Local setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Optional for local testing: configure AWS credentials in `.streamlit/secrets.toml` (copy from `.streamlit/secrets.toml.example`). Without this, responses are written to `local_responses.jsonl`.

3. Run the app:

```bash
streamlit run app.py
```

## DynamoDB setup

DynamoDB does not have spreadsheet-style tabs. The cleanest option for this pilot is a second table, `language_test_responses_v15`. If you prefer one shared table later, the app already writes `test_id` with every response, so exports can be filtered by test.

### 1. Create the table

1. AWS Console → **DynamoDB** → **Create table**
2. Table name: `language_test_responses_v15`
3. Partition key: `session_id` (String)
4. Sort key: `item_id` (String)
5. Capacity: **On-demand**
6. Create table

### 2. Create an IAM user

1. IAM → **Users** → **Create user** (e.g. `streamlit-placement-test`)
2. Add an **inline policy** with:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["dynamodb:PutItem"],
      "Resource": "arn:aws:dynamodb:eu-west-3:*:table/language_test_responses_v15"
    }
  ]
}
```

Replace `eu-west-3` with your region if different.

3. Create **access keys** for the user (Application running outside AWS).

### 3. Streamlit secrets

**Local:** `.streamlit/secrets.toml`

```toml
AWS_ACCESS_KEY_ID = "AKIA..."
AWS_SECRET_ACCESS_KEY = "..."
AWS_REGION = "eu-west-3"
DYNAMODB_TABLE = "language_test_responses_v15"
```

**Streamlit Cloud:** App settings → **Secrets** → paste the same block.

Do not commit `secrets.toml` to Git.

## Deploy to Streamlit Cloud

1. Push this repo to GitHub (without `secrets.toml`).
2. Go to [share.streamlit.io](https://share.streamlit.io/) → **New app**.
3. Select the repo, set main file to `app.py`.
4. Add secrets in the app settings.
5. Deploy.

## Export responses

Use the export script (requires IAM `dynamodb:Scan` on the table — not needed for the app itself):

```bash
pip install boto3
python scripts/export_responses.py
```

Or view items in the DynamoDB Console → **Explore table items**.

## Question file

Edit `English Placement 1.5.csv` to change content. The app:

- Parses each filled question cell after the activity type and input columns as a separate page
- Repeats the row's `Input` stimulus on every page from that row
- Supports `MCQ` and `T/F` rows through the same multiple-choice renderer
- Never shuffles options

## Project layout

```
app.py
English Placement 1.5.csv
src/
  csv_loader.py
  option_parser.py
  renderers.py
  storage.py
  models.py
scripts/
  export_responses.py
```
