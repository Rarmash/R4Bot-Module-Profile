from r4bot_sdk import collect_hook_results


PROFILE_FIELDS_HOOK = "profile.fields"


class ProfileService:
    def __init__(self, module):
        self.module = module
        self.bot = module.bot

    async def collect_extra_fields(self, ctx, member, user_data, server_data):
        collected_fields = []
        results = await collect_hook_results(
            self.bot,
            PROFILE_FIELDS_HOOK,
            ctx=ctx,
            member=member,
            user_data=user_data or {},
            server_data=server_data or {},
        )

        for _, result in results:
            if not result:
                continue

            items = [result] if isinstance(result, dict) else result
            if not isinstance(items, list):
                continue

            for field in items:
                if not isinstance(field, dict):
                    continue
                if "name" not in field or "value" not in field:
                    continue
                collected_fields.append(field)

        return collected_fields
