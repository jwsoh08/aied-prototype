# File can be found
# localhost
# streamlit cloud
# FileNotFoundError
# aws

import streamlit as st
import json
import os
import boto3
from botocore.exceptions import ClientError


from dotenv import load_dotenv

load_dotenv()


class SecretsManager:
    @staticmethod
    def get_secret(key):
        secret_name = "cotf/ai/metacog"
        region_name = "ap-southeast-1"

        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name="secretsmanager",
            region_name=region_name,
        )

        try:
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            # For a list of exceptions thrown, see
            # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
            raise e

        secrets = json.loads(get_secret_value_response["SecretString"])
        return secrets[key]


class SecretsRetriever:
    def get_secret(self, name):
        # currently configured for development and production only
        ENVIRONMENT = os.getenv("ENVIRONMENT")

        if ENVIRONMENT == "DEVELOPMENT":
            return st.secrets[name]
        else:
            return SecretsManager.get_secret(name)


def return_openai_key():
    return st.session_state.openai_key


def return_cohere_key():
    return st.session_state.cohere_key


def return_google_key():
    return st.session_state.google_key


def return_claude_key():
    return st.session_state.claude_key


def return_serp_key():
    return st.session_state.serp_key


def return_assistant_id_1():
    return st.session_state.assistant_id_1
