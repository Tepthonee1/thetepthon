# updater for Tepthon

import asyncio
import sys
from os import environ, execle, path, remove

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

Heroku_APP_NAME = Config.Heroku_APP_NAME or None
Heroku_API_KEY = Config.Heroku_API_KEY or None
UPSTREAM_REPO_BRANCH = Config.UPSTREAM_REPO_BRANCH
UPSTREAM_REPO = "https://github.com/Tepthonee1/thetepthon"
T = Config.COMMAND_HAND_LER

requirements_path = path.join(
    path.dirname(path.dirname(path.dirname(__file__))), "requirements.txt"
)


async def gen_chlog(repo, diff):
    ch_log = ""
    d_form = "%d/%m/%y"
    for c in repo.iter_commits(diff):
        ch_log += (
            f"  • {c.summary} ({c.committed_datetime.strftime(d_form)}) <{c.author}>\n"
        )
    return ch_log


async def print_changelogs(event, ac_br, changelog):
    changelog_str = f"𓆰 sᴏᴜʀᴄᴇ 𝗦𝗔𝗙𝗘𝗧   - 𝑼𝑷𝑫𝑨𝑻𝑬 𝑴𝑺𝑮 𓆪\n 𓍹ⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧ𓍻\n** ⪼ يوجـد تحـديث جديد لسورس سيـفت ༗.**\n\n`{changelog}`\n 𓍹ⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧ𓍻\n 𓆰 𝙎𝙊𝙐𝙍𝘾𝞝 𝘿𝙀𝙑 - @SS22TT 𓆪"
    if len(changelog_str) > 4096:
        await event.edit("`Changelog is too big, view the file to see it.`")
        with open("output.txt", "w+") as file:
            file.write(changelog_str)
        await event.client.send_file(
            event.chat_id,
            "output.txt",
            reply_to=event.id,
        )
        remove("output.txt")
    else:
        await event.client.send_message(
            event.chat_id,
            changelog_str,
            reply_to=event.id,
        )
    return True


async def update_requirements():
    reqs = str(requirements_path)
    try:
        process = await asyncio.create_subprocess_shell(
            " ".join([sys.executable, "-m", "pip", "install", "-r", reqs]),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
        return process.returncode
    except Exception as e:
        return repr(e)


async def deploy(event, repo, ups_rem, ac_br, txt):
    if Heroku_API_KEY is not None:
        import Heroku3

        Heroku = Heroku3.from_key(Heroku_API_KEY)
        Heroku_app = None
        Heroku_applications = Heroku.apps()
        if Heroku_APP_NAME is None:
            await event.edit(
                "`Please set up the` **Heroku_APP_NAME** `Var`"
                " to be able to deploy your sbb_b...`"
            )
            repo.__del__()
            return
        for app in Heroku_applications:
            if app.name == Heroku_APP_NAME:
                Heroku_app = app
                break
        if Heroku_app is None:
            await event.edit(f"{txt}\n" "بيانات اعتماد هيروكو غير صالحة لتنصيب سيـفت")
            return repo.__del__()
        await event.edit(
            "**تنصيب تحديث سيـفت قيد التقدم ، يرجى الانتظار حتى تنتهي العملية ، وعادة ما يستغرق التحديث من 4 إلى 5 دقائق.**"
        )
        ups_rem.fetch(ac_br)
        repo.git.reset("--hard", "FETCH_HEAD")
        Heroku_git_url = Heroku_app.git_url.replace(
            "https://", "https://api:" + Heroku_API_KEY + "@"
        )
        if "Heroku" in repo.remotes:
            remote = repo.remote("Heroku")
            remote.set_url(Heroku_git_url)
        else:
            remote = repo.create_remote("Heroku", Heroku_git_url)
        try:
            remote.push(refspec="HEAD:refs/heads/Heroku", force=True)
        except Exception as error:
            await event.edit(f"{txt}\n`Here is the error log:\n{error}`")
            return repo.__del__()
        build = app.builds(order_by="created_at", sort="desc")[0]
        if build.status == "failed":
            await event.edit(
                "`Build failed!\n" "Cancelled or there were some errors...`"
            )
            await asyncio.sleep(5)
            return await event.delete()
        await event.edit("`Successfully deployed!\n" "Restarting, please wait...`")
    else:
        await event.edit("`Please set up`  **Heroku_API_KEY**  ` Var...`")
    return


async def update(event, repo, ups_rem, ac_br):
    try:
        ups_rem.pull(ac_br)
    except GitCommandError:
        repo.git.reset("--hard", "FETCH_HEAD")
    await update_requirements()
    await event.edit(
        "𓆰 sᴏᴜʀᴄᴇ 𝗦𝗔𝗙𝗘𝗧  - 𝑼𝑷𝑫𝑨𝑻𝑬 𝑴𝑺𝑮 𓆪\n𓍹ⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧ𓍻\n**⪼ تم التحديث بنجاح ✅**\n ** جارٍ إعادة تشغيل بوت سيـفت ، انتظر 𓆰.**"
    )
    # Spin a new instance of bot
    args = [sys.executable, "-m", "sbb_b"]
    execle(sys.executable, *args, environ)
    return


@bot.on(admin_cmd(outgoing=True, pattern=r"تحديث($| (الان|البوت))"))
@bot.on(sudo_cmd(pattern="تحديث($| (الان|البوت))", allow_sudo=True))
async def upstream(event):
    "بالنسبة لأمر التحديث ، تحقق مما إذا كان بوت سيـفت محدثًا ، أو قم بالتحديث إذا تم بتحديثه"
    conf = event.pattern_match.group(1).strip()
    event = await edit_or_reply(
        event,
        "𓆰 sᴏᴜʀᴄᴇ 𝗦𝗔𝗙𝗘𝗧  - 𝑼𝑷𝑫𝑨𝑻𝑬 𝑴𝑺𝑮 𓆪\n 𓍹ⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧ𓍻\n**⪼ جاري البحث عن التحديثات  🌐.. 𓆰،**",
    )
    off_repo = UPSTREAM_REPO
    force_update = False
    if Heroku_API_KEY is None or Heroku_APP_NAME is None:
        return await edit_or_reply(
            event,
            "𓆰 sᴏᴜʀᴄᴇ 𝗦𝗔𝗙𝗘𝗧   - 𝑼𝑷𝑫𝑨𝑻𝑬 𝑴𝑺𝑮 𓆪\n 𓍹ⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧ𓍻\n** ⪼ اضبط المتغيرات المطلوبة أولاً لتحديث بوت سيـفت 𓆰،**",
        )
    try:
        txt = "`عفوًا .. لا يمكن لبرنامج التحديث المتابعة بسبب "
        txt += "حدثت بعض المشاكل`\n\n**تتبع السجل:**\n"
        repo = Repo()
    except NoSuchPathError as error:
        await event.edit(f"{txt}\nالدليل {error} غير موجود")
        return repo.__del__()
    except GitCommandError as error:
        await event.edit(f"{txt}\n`فشل مبكر! {error}`")
        return repo.__del__()
    except InvalidGitRepositoryError as error:
        if conf is None:
            return await event.edit(
                f"`Unfortunately, the directory {error} "
                "does not seem to be a git repository.\n"
                "But we can fix that by force updating the sbb_b using "
                ".update now.`"
            )
        repo = Repo.init()
        origin = repo.create_remote("upstream", off_repo)
        origin.fetch()
        force_update = True
        repo.create_head("Heroku", origin.refs.Heroku)
        repo.heads.Heroku.set_tracking_branch(origin.refs.Heroku)
        repo.heads.Heroku.checkout(True)
    ac_br = repo.active_branch.name
    if ac_br != UPSTREAM_REPO_BRANCH:
        await event.edit(
            "**[UPDATER]:**\n"
            f"`Looks like you are using your own custom branch ({ac_br}). "
            "in that case, Updater is unable to identify "
            "which branch is to be merged. "
            "please checkout to any official branch`"
        )
        return repo.__del__()
    try:
        repo.create_remote("upstream", off_repo)
    except BaseException:
        pass
    ups_rem = repo.remote("upstream")
    ups_rem.fetch(ac_br)
    changelog = await gen_chlog(repo, f"HEAD..upstream/{ac_br}")
    # Special case for deploy
    if conf == "البوت":
        await event.edit(
            "𓆰 sᴏᴜʀᴄᴇ 𝗦𝗔𝗙𝗘𝗧   - 𝑼𝑷𝑫𝑨𝑻𝑬 𝑴𝑺𝑮 𓆪\n𓍹ⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧ𓍻\n**⪼ يتم تنصيب التحديث  انتظر 🌐 𓆰،**"
        )
        await deploy(event, repo, ups_rem, ac_br, txt)
        return
    if changelog == "" and not force_update:
        await event.edit(
            "\n𓆰 sᴏᴜʀᴄᴇ 𝗦𝗔𝗙𝗘𝗧    - 𝑼𝑷𝑫𝑨𝑻𝑬 𝑴𝑺𝑮 𓆪\n𓍹ⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧ𓍻\n**⪼ سورس سيـفت محدث لأخر اصدار ༗. **"
        )
        return repo.__del__()
    if conf == "" and not force_update:
        await print_changelogs(event, ac_br, changelog)
        await event.delete()
        return await event.respond(
            "𓆰 sᴏᴜʀᴄᴇ 𝗦𝗔𝗙𝗘𝗧   - 𝑼𝑷𝑫𝑨𝑻𝑬 𝑴𝑺𝑮 𓆪\n 𓍹ⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧ𓍻\n⪼ اضغط هنا **للتحديث السريع ↫ **[`{}تحديث الان`] او اضغط هنا **لتنصيب التحديث** وقد يستغرق 5 دقائق ↫ [`{}تحديث البوت`]".format(T, T)
        )

    if force_update:
        await event.edit(
            "`Force-Syncing to latest stable Tepthon code, please wait...`"
        )
    if conf == "الان":
        await event.edit(
            "𓆰 sᴏᴜʀᴄᴇ 𝗦𝗔𝗙𝗘𝗧   - 𝑼𝑷𝑫𝑨𝑻𝑬 𝑴𝑺𝑮 𓆪\n 𓍹ⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧ𓍻\n**⪼ يتم تحديث بوت سيـفت  انتظر 🌐..𓆰،**"
        )
        await update(event, repo, ups_rem, ac_br)
    return


CMD_HELP.update(
    {
        "التحديث": "**Plugin : **`التحديث`\n"
        f" • `{T}تحديث` ~ لعرض تحديثات السورس\n"
        f" • `{T}تحديث الان` ~ لتحديث السريع"
    }
)
