from app.ports.history_port import HistoryPort
from app.adapters.database import AsyncSessionLocal, GenerateDocsHistoryModel, ExplainHistoryModel
from sqlalchemy.future import select
from sqlalchemy import delete

class SQLiteHistoryAdapter(HistoryPort):
    """
    Fulfills the HistoryPort contract utilizing explicit asynchronous SQLAlchemy calls.
    """
    
    async def create_generate_docs_history(self, code: str, styles: str, custom_style: str, result: str) -> str:
        async with AsyncSessionLocal() as session:
            new_record = GenerateDocsHistoryModel(
                incoming_code=code,
                styles_used=styles,
                custom_style_used=custom_style,
                ai_response=result
            )
            session.add(new_record)
            await session.commit()
            return new_record.id

    async def create_explain_history(self, code: str, styles: str, custom_style: str, result: str) -> str:
        async with AsyncSessionLocal() as session:
            new_record = ExplainHistoryModel(
                incoming_code=code,
                styles_used=styles,
                custom_style_used=custom_style,
                ai_response=result
            )
            session.add(new_record)
            await session.commit()
            return new_record.id

    async def get_docs_history(self, history_id: str) -> dict | None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(GenerateDocsHistoryModel).where(GenerateDocsHistoryModel.id == history_id))
            record = result.scalars().first()
            if not record:
                return None
            return {
                "id": record.id,
                "incoming_code": record.incoming_code,
                "styles_used": record.styles_used,
                "custom_style_used": record.custom_style_used,
                "ai_response": record.ai_response,
                "createdAT": record.createdAT
            }

    async def get_explain_history(self, history_id: str) -> dict | None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(ExplainHistoryModel).where(ExplainHistoryModel.id == history_id))
            record = result.scalars().first()
            if not record:
                return None
            return {
                "id": record.id,
                "incoming_code": record.incoming_code,
                "styles_used": record.styles_used,
                "custom_style_used": record.custom_style_used,
                "ai_response": record.ai_response,
                "createdAT": record.createdAT
            }

    async def get_all_docs_history(self) -> list:
        async with AsyncSessionLocal() as session:
            # Order by createdAT descending (newest first)
            result = await session.execute(
                select(GenerateDocsHistoryModel.id, GenerateDocsHistoryModel.incoming_code, GenerateDocsHistoryModel.createdAT)
                .order_by(GenerateDocsHistoryModel.createdAT.desc())
            )
            records = result.all()
            return [{"id": str(r.id), "incoming_code": r.incoming_code, "createdAT": r.createdAT} for r in records]

    async def get_all_explain_history(self) -> list:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ExplainHistoryModel.id, ExplainHistoryModel.incoming_code, ExplainHistoryModel.createdAT)
                .order_by(ExplainHistoryModel.createdAT.desc())
            )
            records = result.all()
            return [{"id": str(r.id), "incoming_code": r.incoming_code, "createdAT": r.createdAT} for r in records]

    async def clear_all_history(self) -> dict:
        async with AsyncSessionLocal() as session:
            await session.execute(delete(GenerateDocsHistoryModel))
            await session.execute(delete(ExplainHistoryModel))
            await session.commit()
            return {"status": "success", "message": "All database history safely destroyed."}

    async def delete_docs_history(self, history_id: str) -> bool:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                delete(GenerateDocsHistoryModel).where(GenerateDocsHistoryModel.id == history_id)
            )
            await session.commit()
            return result.rowcount > 0

    async def delete_explain_history(self, history_id: str) -> bool:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                delete(ExplainHistoryModel).where(ExplainHistoryModel.id == history_id)
            )
            await session.commit()
            return result.rowcount > 0
