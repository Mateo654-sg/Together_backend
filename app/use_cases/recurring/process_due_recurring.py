"""
Use Case: ProcessDueRecurringTransactions (FR-033-Process).

Materializa los movimientos recurrentes vencidos en gastos o ingresos
personales y avanza la próxima ejecución según la frecuencia.
"""

import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.personal_expense import PersonalExpense
from app.models.personal_income import PersonalIncome
from app.repositories.personal_expense_repository import PersonalExpenseRepository
from app.repositories.personal_income_repository import PersonalIncomeRepository
from app.repositories.recurring_transaction_repository import RecurringTransactionRepository
from app.schemas.recurring_transaction import ProcessRecurringResponse
from app.use_cases.recurring.schedule import next_execution_date


class ProcessDueRecurringTransactionsUseCase:
    """Use Case: ProcessDueRecurringTransactions (FR-033-Process).

    Convierte recurrencias vencidas en movimientos reales y reprograma
    la siguiente ejecución.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = RecurringTransactionRepository(session)
        self.expense_repo = PersonalExpenseRepository(session)
        self.income_repo = PersonalIncomeRepository(session)

    async def execute(
        self, user_id: uuid.UUID, on_date: date | None = None
    ) -> ProcessRecurringResponse:
        """Procesa las recurrencias vencidas.

        Args:
            user_id: UUID del usuario propietario.
            on_date: Fecha de referencia (por defecto hoy).

        Returns:
            ProcessRecurringResponse con la cantidad de movimientos generados.
        """
        today = on_date or date.today()
        due = await self.repository.list_due(user_id, today)

        details = []
        for recurrence in due:
            if recurrence.type == "expense":
                movement = PersonalExpense(
                    user_id=user_id,
                    category_id=recurrence.category_id,
                    amount=recurrence.amount,
                    description=recurrence.description,
                    expense_date=recurrence.next_execution,
                )
                await self.expense_repo.create(movement)
            else:
                movement = PersonalIncome(
                    user_id=user_id,
                    category_id=recurrence.category_id,
                    amount=recurrence.amount,
                    description=recurrence.description,
                    income_date=recurrence.next_execution,
                )
                await self.income_repo.create(movement)

            recurrence.last_executed = recurrence.next_execution
            recurrence.next_execution = next_execution_date(
                recurrence.frequency, recurrence.next_execution
            )
            details.append(
                {
                    "recurring_id": str(recurrence.id),
                    "type": recurrence.type,
                    "amount": float(recurrence.amount),
                    "executed_on": recurrence.last_executed.isoformat(),
                    "next_execution": recurrence.next_execution.isoformat(),
                }
            )

        await self.session.commit()
        return ProcessRecurringResponse(executed=len(details), details=details)
