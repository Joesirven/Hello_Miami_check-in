import os
from supabase import create_client, Client, ClientOptions
from dotenv import load_dotenv

load_dotenv()


class DatabaseConfig:
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

    @classmethod
    def print_config(cls):
        print(f"SUPABASE_URL: {cls.SUPABASE_URL}")
        print(
            f"SUPABASE_KEY: {'*' * len(cls.SUPABASE_KEY) if cls.SUPABASE_KEY else 'Not set'}"
        )


class SupabaseClient:
    def __init__(self):
        self.client: Client = create_client(
            DatabaseConfig.SUPABASE_URL,
            DatabaseConfig.SUPABASE_KEY,
            options=ClientOptions(
                postgrest_client_timeout=10,
                storage_client_timeout=10,
                schema="public",
            )
        )

    async def test_connection(self):
        print("Testing Supabase connection...")
        try:
            response = self.client.table('test table').select('*').execute()
            print("Supabase connection successful")
            print(f"Response: {response}")
            return response
        except Exception as e:
            print(f"Supabase connection failed: {str(e)}")
            return None


# Create instance
supabase_client = SupabaseClient()

# You can keep the __main__ block if you want to test the connection
if __name__ == "__main__":
    import asyncio
    DatabaseConfig.print_config()
    asyncio.run(supabase_client.test_connection())
