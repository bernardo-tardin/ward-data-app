# Gestão Inteligente e Inovadora de Enfermarias: Solução para Continuação de Cuidados

![Python Version](https://img.shields.io/badge/python-3.11-blue)
![Django Version](https://img.shields.io/badge/django-4.2-darkgreen)
![Docker Supported](https://img.shields.io/badge/docker-%20compatible-blue?logo=docker)
![License](https://img.shields.io/badge/license-MIT-green)

Sistema de contingência para garantir acesso contínuo a dados clínicos durante períodos de *downtime* de Registos Eletrónicos de Saúde (EHR).

---

## 📄 Sobre o Projeto

Este repositório contém o código-fonte desenvolvido como parte da **Dissertação de Mestrado em Engenharia Biomédica** (Ramo: Informática Médica) da **Universidade do Minho**.

* **Autor:** Bernardo Tardin de Moraes
* **Orientadores:**
    * Prof. Doutor Hugo Daniel Abreu Peixoto
    * Profª. Doutora Ana Regina Coelho de Sousa
* **Ano:** 2025
* **Instituição:** Escola de Engenharia, Universidade do Minho, Braga, Portugal

📚 **Dissertação completa:** (disponível após aprovação)

---

## 🎯 Objetivo

O sistema foi desenvolvido para mitigar os riscos associados a períodos de indisponibilidade (*downtime*) dos sistemas EHR hospitalares, causados por manutenções programadas, falhas técnicas ou ciberataques.

A solução oferece **duas modalidades complementares** de acesso à informação clínica:

1.  **Interface Web:** Consulta em tempo real dos dados dos utentes internados, com filtros contextuais por **especialidade** (ou visualização de **todas** as especialidades).
2.  **Sistema de Contingência Offline:** Exportação automática e periódica de relatórios clínicos em formato PDF, organizados hierarquicamente por **especialidade**, **sala** e **cama/utente** (`<Especialidade>/<Sala>/<Cama>_<ID-Episódio>_<Nome-Utente>.pdf`), garantindo acesso mesmo durante falhas totais do sistema principal.

---

## ✨ Características Principais

* **🏗️ Arquitetura Modular e Configurável:**
    * Camada de Acesso a Dados (DAL) agnóstica ao esquema da base de dados.
    * Adaptação a diferentes infraestruturas via ficheiro JSON externo.
    * Suporte para Oracle, PostgreSQL, SQL Server sem alteração de código.
* **⚡ Processamento Assíncrono Resiliente:**
    * Sistema de tarefas em *background* com Celery e RabbitMQ.
    * Exportação periódica automatizada de relatórios PDF.
    * Mecanismo de retentativa automática em caso de falhas.
    * Escalabilidade horizontal através de múltiplos *workers*.
* **🔒 Segurança e Isolamento:**
    * Arquitetura multi-base de dados com acesso *read-only* à base hospitalar.
    * Isolamento entre dados operacionais (SQLite) e dados clínicos.
    * Sistema de autenticação e gestão de estado por sessão.
* **🐳 Deployment Simplificado:**
    * Containerização completa com Docker.
    * Orquestração de serviços com Docker Compose.
    * Ambiente reprodutível e portátil.
* **📊 Interface Intuitiva:**
    * Seleção contextual por especialidade ou visualização global.
    * Pesquisa (ID/Nome) e paginação de utentes.
    * Geração de relatórios *on-demand*.

---

## 🏆 Resultados de Validação

A solução foi avaliada através de metodologia mista com profissionais técnicos experientes em sistemas hospitalares, utilizando dados reais.

| Dimensão                  | Métrica             | Resultado           | Classificação |
| :------------------------ | :------------------ | :------------------ | :------------ |
| Usabilidade               | SUS                 | **71.7 / 100*** | Bom (B)       |
| Utilidade Percebida       | TAM/UTAUT           | **86.7%** concord.  | Elevada       |
| Eficiência - Interface Web | Escala Likert (1-5) | **4.22 / 5.0** | Muito Boa     |
| Eficiência - Contingência PDF | Escala Likert (1-5) | **4.22 / 5.0** | Muito Boa     |
| Satisfação Global         | Escala 1-10†        | **7.67 / 10** | Satisfeito    |
<br/>
<small>*Pontuação SUS (escala 0-100)</small>
<small>†Escala 1-10</small>


### 🎖️ Destaques da Avaliação

* ✅ Pontuação SUS **acima da média de referência** (68 pontos).
* ✅ **Concordância unânime** sobre facilitação de acesso em situações críticas (Item 13, M=4.67).
* ✅ **Equivalência estatística** entre eficiência dos cenários *online* (M=4.22) e *offline* (M=4.22).
* ✅ **100% de concordância** sobre organização hierárquica dos ficheiros PDF (Item 21, M=4.33).

*Detalhes completos no Capítulo 6 da dissertação.*

---

## 🛠️ Stack Tecnológica

* **Backend:** Python 3.11, Django 4.2, Celery 5.3, RabbitMQ, WeasyPrint
* **Frontend:** Django Templates (SSR), HTML5/CSS3, JavaScript (vanilla)
* **Base de Dados:** SQLite (interna), Oracle / PostgreSQL / SQL Server (externa)
* **Infrastructure:** Docker & Docker Compose, Nginx, Gunicorn

---

## 📋 Pré-requisitos

Antes de começar, garanta que tem o seguinte instalado e configurado:

1.  **Docker Engine:** Versão 20.10 ou superior. [Instruções de Instalação](https://docs.docker.com/engine/install/)
2.  **Docker Compose:** Versão 2.0 ou superior (geralmente incluído com o Docker Desktop). [Instruções de Instalação](https://docs.docker.com/compose/install/)
3.  **Acesso à Base de Dados Hospitalar:**
    * Credenciais de um utilizador com permissões de **leitura (read-only)**.
    * Detalhes da conexão (Host/IP, Porta, Nome do Serviço/SID - **recomendado Service Name**).
    * **VPN Ativa:** Se a base de dados não for acessível publicamente, certifique-se de que a sua conexão VPN (ex: GlobalProtect) está ativa e configurada corretamente.
4.  **Recursos do Sistema:**
    * Mínimo 4GB de RAM disponível para os contentores Docker.
    * Espaço em disco suficiente para a imagem Docker, dependências e, crucialmente, para o armazenamento dos ficheiros PDF gerados (depende do número de utentes e frequência de backup).

---

## 🚀 Instalação e Configuração Detalhada

### 1. Clonar o Repositório

Abra o seu terminal e clone o repositório para a sua máquina local:
```bash
git clone [https://github.com/](https://github.com/)[seu-usuario]/ward-data-portal.git
cd ward-data-portal
````

### 2\. Configurar Variáveis de Ambiente (`.env`)

Este é um passo crucial para a segurança e funcionamento da aplicação. Copie o ficheiro de exemplo:

```bash
# Linux/macOS
cp .env.example .env
# Windows
copy .env.example .env
```

Agora, **edite o ficheiro `.env`** que acabou de criar na raiz do projeto. Preencha **todas** as variáveis. Consulte a secção **Configuração Avançada (`.env`)** abaixo para detalhes sobre cada variável. As mais importantes são:

  * `DJANGO_SECRET_KEY`: Gere uma nova chave aleatória.
  * `DB_TYPE`: `oracle`, `postgres` ou `sqlserver`.
  * Credenciais da BD Externa (`SQL_DSN` ou `SQL_HOST`/`PORT`/`DB_NAME`, `SQL_USER`, `SQL_PASSWORD`).
  * `HOST_BACKUP_DIR`: Caminho na sua máquina onde os PDFs serão guardados.

🔐 **Gerar chave secreta Django:**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3\. Configurar Queries da Base de Dados (`config.json`)

⚠️ **PASSO CRÍTICO:** Este ficheiro mapeia a lógica da aplicação ao esquema específico da sua base de dados.

  * Abra o ficheiro `configs/config.json`.
  * **Reescreva TODAS as queries SQL** na secção `"queries"` para funcionarem com a sua base de dados.
  * Verifique e ajuste os mapeamentos na secção `"columns"`.

📖 **Instruções detalhadas e exemplos:** Consulte a secção **Configuração Avançada (`config.json`)** abaixo para um guia completo. **A aplicação NÃO FUNCIONARÁ se este passo não for feito corretamente.**

### 4\. Construir a Imagem Docker

Este comando irá construir a imagem da aplicação, instalando as dependências corretas com base no `DB_TYPE` que definiu no `.env`. Execute no terminal, na raiz do projeto:

```bash
# Substitua 'oracle' pelo seu DB_TYPE se for diferente
docker compose build --build-arg DB_TYPE=oracle
```

*Este processo pode demorar alguns minutos na primeira vez.*

### 5\. Iniciar os Serviços

Execute o seguinte comando para iniciar todos os contentores (Nginx, Django, Celery, RabbitMQ) em background:

```bash
docker compose up -d
```

Aguarde um pouco até que todos os serviços estejam a funcionar (pode verificar com `docker compose ps`).

### 6\. Criar Utilizador Administrador

Para poder aceder à aplicação, crie a primeira conta de utilizador (administrador):

```bash
docker compose exec web python manage.py createsuperuser
```

Siga as instruções no terminal para definir um nome de utilizador, email (opcional) e password.

-----

## ⚙️ Configuração Avançada

### Variáveis de Ambiente (`.env`)

O ficheiro `.env`, localizado na raiz do projeto, controla o comportamento da aplicação e dos seus serviços. Certifique-se de que este ficheiro **não é versionado** no Git por questões de segurança.

  * `DJANGO_SECRET_KEY`: **Obrigatório.** Chave secreta única para a sua instância Django.
  * `DB_TYPE`: **Obrigatório.** Define o tipo de base de dados externa (`oracle`, `postgres`, `sqlserver`). Usado no build.
  * **Configuração da Base de Dados Externa:**
      * **Método 1: DSN (Recomendado Oracle com Service Name)**
          * `SQL_DSN`: String de conexão TNS completa. Ex: `"(DESCRIPTION=(...)(SERVICE_NAME=aida))"`
          * `SQL_USER`, `SQL_PASSWORD`: Credenciais read-only.
          * *Deixe `SQL_HOST`, `SQL_PORT`, `SQL_DB_NAME` vazios.*
      * **Método 2: Campos Separados (Postgres, SQL Server, Oracle com SID)**
          * `SQL_HOST`, `SQL_PORT`, `SQL_DB_NAME`: Detalhes da conexão.
          * `SQL_USER`, `SQL_PASSWORD`: Credenciais read-only.
          * *Deixe `SQL_DSN` vazio.*
  * `CELERY_BROKER_URL`: URL do RabbitMQ (formato: `amqp://user:pass@host:port/vhost`). Padrão: `amqp://admin:admin123@rabbitmq:5672/`
  * `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS`: Credenciais para a interface de gestão do RabbitMQ. Use passwords seguras.
  * `HOSPITAL_CONFIG_PATH`: Caminho *dentro do container* para `config.json` (Padrão: `configs/config.json`). Não alterar geralmente.
  * `BACKUP_INTERVAL`: Frequência do backup automático (em segundos). Padrão: `7200` (2 horas).
  * `HOST_BACKUP_DIR`: Caminho absoluto **na sua máquina (host)** para guardar os PDFs. Ex: `~/Desktop/pdfs_backup` ou `C:/Users/User/Documents/pdfs_backup`.
  * `OFFLINE_BACKUP_DIR`: Caminho *dentro do container* onde a app escreve PDFs (Padrão: `/app/pdfs`). **Não alterar**.
  * `DJANGO_ALLOWED_HOSTS`: Hosts permitidos (separados por vírgula). Ex: `localhost,127.0.0.1,meudominio.com`.
  * `DJANGO_DEBUG`: `True` (desenvolvimento) ou `False` (produção).

### Configuração das Queries (`config.json`)

⚠️ **ESTE FICHIRO É CRÍTICO.** Adapte-o ao seu ambiente hospitalar.

**Estrutura:**

```json
{
  "queries": { "chave_interna": "SELECT ...", ... },
  "columns": { "chave_interna_app": "NOME_COLUNA_BD", ... },
  "sorting": { "contexto": { "chave_app": "NOME_COLUNA_BD_SORT" } },
  "parameters": { "chave": "valor_constante" }
}
```

**Regras Obrigatórias:**

1.  **Nomes das Colunas:** As suas queries **DEVEM** retornar colunas com os nomes **EXATOS** que estão definidos como **VALORES** na secção `"columns"`. Use `AS` se necessário.
2.  **Parâmetros:** Utilize **SEMPRE `%s`** como marcador de posição. O sistema converte para `?` se `DB_TYPE=sqlserver`. A **ordem** dos `%s` deve corresponder à ordem dos parâmetros listados abaixo.

**Referência Detalhada das Queries:**

Aqui está a descrição de cada *query* esperada, os parâmetros que a aplicação irá passar (na ordem correta) e as colunas de saída obrigatórias (os nomes referem-se aos **valores** na secção `"columns"`).

-----

  * **`get_specialties`**
      * **Propósito:** Lista de especialidades para o menu de seleção.
      * **Parâmetros:** Nenhum.
      * **Colunas Obrigatórias:** `COD_ESPECIALIDADE`, `DES_ESPECIALIDADE`.

-----

  * **`get_recent_patients`**
      * **Propósito:** Busca os 10 utentes mais recentes (base query).
      * **Parâmetros:**
        1.  `specialty_id` (Opcional - adicionado dinamicamente pela DAL se fornecido).
      * **Colunas Obrigatórias:** `INT_EPISODIO`, `COD_SALA`, `NUM_CAMA`, `NOME`.

-----

  * **`get_patient_list_base`**
      * **Propósito:** Base para a lista paginada de utentes.
      * **Parâmetros:** Nenhum (filtros e paginação são adicionados dinamicamente pela DAL).
      * **Colunas Obrigatórias:** `INT_EPISODIO`, `COD_SALA`, `NUM_CAMA`, `DTA_ENTRADA`, `HORA_ENTRADA`, `NOME`.

-----

  * **`get_patient_list_count_base`**
      * **Propósito:** Base para contar o total de utentes (para paginação).
      * **Parâmetros:** Nenhum (filtros são adicionados dinamicamente pela DAL).
      * **Colunas Obrigatórias:** `TOTAL`.

-----

  * **`get_patient_details`**
      * **Propósito:** Busca dados de cabeçalho e especialidade de um utente (base query).
      * **Parâmetros:**
        1.  `patient_id` (ID do episódio).
        2.  `specialty_id` (Opcional - adicionado dinamicamente pela DAL se fornecido para validação).
      * **Colunas Obrigatórias:** `INT_EPISODIO`, `DTA_ENTRADA`, `HORA_ENTRADA`, `COD_SALA`, `NUM_CAMA`, `NOME`, `DES_ESPECIALIDADE`.

-----

  * **`get_patient_id_by_name`**
      * **Propósito:** Encontra o ID do utente mais recente por nome (base query).
      * **Parâmetros:**
        1.  `specialty_id` (Opcional - adicionado dinamicamente pela DAL se fornecido).
        2.  `patient_name` (Para a cláusula `LIKE`).
      * **Colunas Obrigatórias:** `INT_EPISODIO`.

-----

  * **`get_all_patient_ids`**
      * **Propósito:** Lista todos os IDs para o backup periódico (base query).
      * **Parâmetros:**
        1.  `specialty_id` (Opcional - adicionado dinamicamente pela DAL se um backup por especialidade for implementado no futuro).
      * **Colunas Obrigatórias:** `INT_EPISODIO`.

-----

  * **Queries Dependentes Apenas de `patient_id` (ID do Episódio):**
      * `get_ainicial_items`: **Params:** `patient_id`, `antecedentes_code`, `diagnostico_code`. **Cols:** `ITEM`, `VALOR`.
      * `get_telefone`: **Params:** `patient_id`. **Cols:** `TEL_MORADA`, `NR_TELM`.
      * `get_pessoa_signif`: **Params:** `patient_id`. **Cols:** `PESSOA`.
      * `get_observacoes`: **Params:** `patient_id`. **Cols:** `OBSERVACOES`.
      * `get_fenomenos`: **Params:** `patient_id`. **Cols:** `DATA_INICIO_FENOM`, `HORA_INICIO_FENOM`, `FENOMENO_PT`, `ESPECIFICACAO`.
      * `get_medicacao`: **Params:** `patient_id`. **Cols:** `DOSE`, `HORARIO`, `FARMACO`, `VIA`.
      * `get_atitudes`: **Params:** `patient_id`. **Cols:** `ATITUDETERAPEUTICA`, `HORARIO_ATITUDE`.
      * `get_analises`: **Params:** `patient_id`. **Cols:** `ANALISE`, `DATA_INICIO_ANALISE`, `HORA_INICIO_ANALISE`.
      * `get_exames`: **Params:** `patient_id`. **Cols:** `EXAME`, `DATA_MARCACAO`.
      * `get_diarios`: **Params:** `patient_id`. **Cols:** `DATA_DIARIO`, `HORA_DIARIO`, `DIARIO`.
      * `get_ultimo_diario_chave`: **Params:** `patient_id`. **Cols:** `DATA_DIARIO`, `HORA_DIARIO`.
      * `get_ultimo_diario_texto`: **Params:** `patient_id`, `data_ultimo_diario`, `hora_ultimo_diario`. **Cols:** `ULT_DIARIO`.

-----

**Exemplo Completo (`config.json`):**
Consulte o ficheiro `configs/config.example.json` no repositório para um exemplo completo da estrutura esperada.

-----

## 🌐 Acesso aos Serviços

| Serviço               | URL                     | Descrição                    |
| :-------------------- | :---------------------- | :--------------------------- |
| **Aplicação Web** | `http://localhost:8000`   | Interface principal          |
| **Admin Django** | `http://localhost:8000/admin` | Gestão de utilizadores       |
| **RabbitMQ Management** | `http://localhost:15672`  | Monitorização de filas Celery |

**Credenciais RabbitMQ:** Use as definidas em `RABBITMQ_DEFAULT_USER` / `RABBITMQ_DEFAULT_PASS` no seu `.env`.

-----

## 📐 Arquitetura Técnica Detalhada

### 1\. Visão Geral

Aplicação web modular e resiliente para consulta de dados clínicos e contingência offline via PDFs. Arquitetura baseada em microserviços orquestrados por Docker Compose.

**Componentes:** Nginx (Proxy), Django/Gunicorn (Web App), Celery Worker(s) (Tarefas Background), Celery Beat (Agendador), RabbitMQ (Fila), SQLite (BD Interna), BD Hospitalar (Externa).

### 2\. Decisões Arquitetónicas Chave

  * **Camada de Acesso a Dados (DAL) Modular (`dal.py`):** Isola acesso à BD externa, configurável via `config.json` (queries, colunas), usa queries parametrizadas, padroniza dados internamente. Lógica dinâmica para filtros (`specialty_id`), ordenação e paginação.
  * **Arquitetura Multi-Base de Dados (`settings.py`, `dbrouters.py`):** Garante acesso *read-only* à BD hospitalar (`hospital`) e usa BD interna (`default` - SQLite) para utilizadores/sessões. `HospitalRouter` direciona queries e bloqueia escritas/migrações na BD externa.
  * **Processamento Assíncrono (`celery.py`, `tasks.py`):** Celery/RabbitMQ para tarefas longas (geração PDFs) sem bloquear a interface. Celery Beat agenda backups periódicos (`BACKUP_INTERVAL`). Padrão Fan-Out (`gerar_backup_pdfs_periodico` -\> N x `gerar_pdf_para_utente`) para resiliência e paralelismo. Tarefa `gerar_pdf_para_utente` inclui retentativas (`self.retry`).
  * **Geração de PDFs (`pdf_utils.py`, `tasks.py`, `patient-pdf.html`):** WeasyPrint converte HTML+CSS (gerado por template Django) para PDF. Armazenamento hierárquico (`<Especialidade>/<Sala>/<Cama>_<ID>_<Nome>.pdf`).
  * **Containerização e Orquestração (`Dockerfile`, `docker-compose.yml`):**
      * `Dockerfile`: Multi-stage build, instalação condicional de cliente BD (`ARG DB_TYPE`), utilizador não-root (`app`).
      * `docker-compose.yml`: Define serviços, volumes dinâmicos (PDFs via `${HOST_BACKUP_DIR}`), rede interna, healthchecks e `depends_on: condition: service_healthy`.
  * **Gestão de Estado (`views.py`, Sessões Django):** Seleção de contexto (especialidade ou "Ver Todos") guardada na sessão (`selected_specialty_id`, `selected_specialty_name`). Views verificam `selected_specialty_name` para acesso e passam `selected_specialty_id` (ou `None`) para a DAL filtrar dados.

-----

## 🚀 Deployment em Produção (Notas)

Implementar em produção requer cuidados adicionais. Pontos principais:

  * **Servidor:** Linux com Docker/Compose, recursos adequados.
  * **Configuração `.env`:** Usar ficheiro específico de produção (`DJANGO_DEBUG=False`, `ALLOWED_HOSTS` corretos, passwords fortes). Considerar gestão de segredos.
  * **Nginx:** Configurar HTTPS (SSL/TLS), servir ficheiros estáticos, headers de segurança.
  * **Gunicorn:** Ajustar número de `workers`/`threads` consoante os recursos do servidor.
  * **Celery:** Ajustar `concurrency`, escalar `workers` se necessário. Monitorizar filas (RabbitMQ UI, Flower).
  * **Persistência e Backups:** O diretório `HOST_BACKUP_DIR` **DEVE** estar incluído na rotina de backups do hospital. Fazer backup do volume `rabbitmq_data` e do ficheiro `db.sqlite3`.
  * **Logging/Monitorização:** Centralizar logs, monitorizar recursos dos contentores.
  * **Processo de Atualização:** `git pull`, `docker compose build` (se necessário), `migrate`, `collectstatic`, `docker compose down && docker compose up -d`.
  * **Validação:** Testes extensivos com utilizadores finais, plano de contingência, conformidade RGPD/legislação.

-----

## 🔧 Comandos Úteis

**Gestão de Serviços:**

```bash
# Parar todos os serviços
docker compose down

# Parar e remover volumes (CUIDADO: apaga dados do RabbitMQ e SQLite interno)
docker compose down --volumes

# Reiniciar um serviço específico
docker compose restart web

# Ver logs de um serviço
docker compose logs -f celery

# Executar comando Django (ex: migrações da BD interna)
docker compose exec web python manage.py migrate
```

**Gestão de Utilizadores:**

```bash
# Criar superutilizador
docker compose exec web python manage.py createsuperuser

# Criar outros utilizadores via admin: http://localhost:8000/admin
```

**Otimização de Performance:**

  * **Aumentar processos por worker Celery:** Edite `docker-compose.yml` e adicione `--concurrency=N` ao `command` do serviço `celery`.
  * **Escalar workers horizontalmente:** `docker compose up -d --scale celery=3` (para 3 workers).

-----

## 🧪 Testes (Exemplo)

```bash
# Executar suite de testes (se configurada)
docker compose exec web python manage.py test

# Executar com coverage (se configurado)
docker compose exec web coverage run --source='.' manage.py test
docker compose exec web coverage report
```

-----

## 🐛 Troubleshooting

  * **Problema: Aplicação não inicia**
      * Verifique os logs: `docker compose logs web`
      * Verifique a conectividade à BD externa a partir do container:
        ```bash
        docker compose exec web bash
        # Dentro do container, tente usar nc ou telnet, se disponíveis
        nc -zv <HOST_DA_BD> <PORTA_DA_BD>
        exit
        ```
      * Confirme se a VPN está ativa (se necessário).
  * **Problema: PDFs não são gerados**
      * Verifique os logs do Celery: `docker compose logs celery`
      * Verifique a fila RabbitMQ: Aceda a `http://localhost:15672`
  * **Problema: Queries SQL falham (`ORA-xxxx`, etc.)**
      * Verifique se as colunas de *output* e nomes em `configs/config.json` correspondem exatamente ao esperado.
      * Confirme a compatibilidade da sintaxe SQL com o seu SGBD.
      * Teste as *queries* diretamente na base de dados.
      * Verifique se as credenciais no `.env` (especialmente `SQL_DSN`) estão corretas.

-----

## 📊 Estrutura do Projeto

```
ward-data-portal/
├── configs/
│   ├── config.json               # ⚠️ Ficheiro de configuração REAL (editar aqui)
├── dadosenfermaria/              # Aplicação Django principal
│   ├── migrations/               # Migrações da BD interna (SQLite)
│   ├── templates/                # Templates HTML
│   │   └── dadosenfermaria/
│   │       ├── select-specialty.html # Nova página de seleção
│   │       ├── ... (outros templates)
│   ├── dal.py                    # Data Access Layer (lógica BD externa)
│   ├── tasks.py                  # Tarefas Celery (geração PDF)
│   ├── views.py                  # Views Django (lógica HTTP)
│   ├── pdf_utils.py              # Utilitários de formatação para PDF
│   └── ... (outros ficheiros da app)
├── project/                      # Configuração global do projeto Django
│   ├── settings.py               # Configurações principais
│   ├── celery.py                 # Configuração do Celery
│   ├── dbrouters.py              # Router para multi-BD
│   └── urls.py                   # Mapeamento de URLs
├── static/                       # Ficheiros estáticos (CSS, JS)
│   ├── css/
│   └── js/
├── nginx/                        # Configuração do Nginx
│   └── nginx.conf
├── Dockerfile                    # Instruções para construir a imagem Docker
├── docker-compose.yml            # Orquestração dos serviços
├── requirements.txt              # Dependências Python
├── manage.py                     # Utilitário de gestão Django
├── .env.example                  # Template das variáveis de ambiente
├── .env                          # ⚠️ Ficheiro real das variáveis (NÃO versionar)
├── .gitignore
├── LICENSE
└── README.md                     # Este ficheiro
```

-----

## 🤝 Contribuições

Este projeto foi desenvolvido num contexto académico. Contribuições, *forks* e sugestões são bem-vindas, especialmente nas seguintes áreas:

  * 🌍 Internacionalização (i18n) da interface.
  * 🔐 Integração com sistemas de SSO (LDAP, SAML).
  * 🔌 Suporte para standards de interoperabilidade (HL7 FHIR).
  * ✅ Expansão da cobertura de testes automatizados.

-----

## 📝 Licença

Este projeto está licenciado sob a **MIT License** - consulte o ficheiro `LICENSE` para detalhes.

-----

## 📖 Citação

Se utilizar este trabalho na sua investigação ou projeto, por favor cite:

**BibTeX:**

```bibtex
@mastersthesis{moraes2025ward,
  author  = {Moraes, Bernardo Tardin de},
  title   = {Gestão Inteligente e Inovadora de Enfermarias: Solução para Continuação de Cuidados},
  school  = {Universidade do Minho},
  year    = {2025},
  address = {Braga, Portugal},
  type    = {Dissertação de Mestrado},
  note    = {Mestrado em Engenharia Biomédica (Informática Médica)}
}
```

-----

## 📧 Contacto

  * **Bernardo Tardin de Moraes:** pg53700@alunos.uminho.pt
  * **Instituição:** Universidade do Minho - Escola de Engenharia

-----

## ⚠️ Aviso Legal

Este sistema foi desenvolvido para fins académicos e de investigação. A sua implementação em ambiente de produção hospitalar deve ser precedida de auditoria de segurança completa, validação clínica por profissionais de saúde no contexto real, cumprimento da regulamentação (RGPD, legislação nacional) e processos de certificação apropriados. O autor e a Universidade do Minho não se responsabilizam por implementações inadequadas ou uso indevido do sistema.

```
```