-- Reference schema for Redis checkpointer (managed by langgraph-checkpoint-redis).
-- If using PostgreSQL, swap RedisSaver for PostgresSaver in agent_factory.py.
-- This file is for ops reference only — no execution required for MVP deploy.

-- Redis keyspace used automatically:
--   checkpoint:{thread_id}:*      → graph state snapshots
--   checkpoint_write:{thread_id}  → write-ahead log