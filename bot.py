# ────────────────────────────────
# ✅ Discord 인증 봇 (Koyeb 버전)
# ────────────────────────────────
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

# ────────────────────────────────
# ✅ 환경 변수 설정
# ────────────────────────────────
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CORRECT_CODE = os.getenv("DISCORD_CORRECT_CODE")


# ────────────────────────────────
# ✅ 설정 상수
# ────────────────────────────────
CHANNEL_ID = 1294924228600270890  # 인증 채널 ID
MAX_ATTEMPTS = 3

# 역할 이름
CLUB_ROLE = "클럽원"
OTHER_ROLES = ["쟁탈원", "관리자"]
ALL_ROLES = [CLUB_ROLE] + OTHER_ROLES

# 사용자 인증 시도 기록
user_attempts = {}

# ────────────────────────────────
# ✅ 봇 초기화
# ────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


def has_any_role(member: discord.Member) -> bool:
    """사용자가 특정 역할 중 하나라도 가지고 있는지 확인"""
    return any(discord.utils.get(member.roles, name=role) for role in ALL_ROLES)


# ────────────────────────────────
# ✅ 이벤트 핸들러
# ────────────────────────────────
@bot.event
async def on_ready():
    print(f"✅ 봇 로그인 성공: {bot.user}")


@bot.event
async def on_message(message):
    if message.author.bot or message.channel.id != CHANNEL_ID:
        return

    member = message.author
    guild = message.guild
    content = message.content.strip()

    # 정답 입력
    if content == CORRECT_CODE:
        try:
            await message.delete()
        except discord.Forbidden:
            print("❗ 메시지 삭제 권한 부족")

        if has_any_role(member):
            await message.channel.send(f"{member.mention} 당신은 이미 역할을 갖고 있습니다.")
            return

        role = discord.utils.get(guild.roles, name=CLUB_ROLE)
        if role:
            await member.add_roles(role)
            await message.channel.send(f"{member.mention} {CLUB_ROLE} 역할이 부여되었습니다.")
        else:
            await message.channel.send(f"❗ '{CLUB_ROLE}' 역할이 존재하지 않습니다.")

        user_attempts.pop(member.id, None)
        return

    # 이미 역할이 있는 경우
    if has_any_role(member):
        await message.channel.send(f"{member.mention} 당신은 이미 역할을 갖고 있습니다.")
        return

    # 첫 시도 안내
    if member.id not in user_attempts:
        user_attempts[member.id] = 0
        await message.channel.send(
            f"🎉{member.mention} 삐약에 오신 것을 환영합니다.\n"
            f"🥳역할 부여를 위한 가입인증 코드는?\n"
            f"🥳답은 톡방 공지사항에 있습니다. 채팅으로 답을 남겨주세요."
        )
        return

    # 오답 처리
    user_attempts[member.id] += 1
    attempts = user_attempts[member.id]

    if attempts >= MAX_ATTEMPTS:
        await message.channel.send(f"{member.mention} 인증 코드 3회 오류로 서버에서 강퇴됩니다.")
        try:
            await guild.kick(member, reason="인증 실패 (3회 오답)")
        except discord.Forbidden:
            await message.channel.send("⚠️ 강퇴 실패: 권한 부족")
        user_attempts.pop(member.id, None)
    else:
        await message.channel.send(
            f"{member.mention} 인증 코드가 틀렸습니다. ({attempts}회 실패)\n"
            f"3회 실패 시 강퇴됩니다."
        )


# ────────────────────────────────
# ✅ 봇 실행
# ────────────────────────────────
bot.run(TOKEN)
