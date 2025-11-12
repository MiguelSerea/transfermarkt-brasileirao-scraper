from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re
from datetime import datetime
import os

class TransfermarktBase:
    """Classe base com funcionalidades comuns"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.default_save_path = r"C:\Users\migue\trabalho\análise de dados\selenium\talentos jovens\Data"
    
    def setup_driver(self):
        """Configuração do WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)
        return self.driver
    
    def handle_iframe_popup(self):
        """Trata o popup dentro do iframe"""
        try:
            print("   🍪 Procurando iframe do popup...")
            time.sleep(3)
            
            try:
                print("   🔍 Tentando iframe sourcepoint...")
                iframe = WebDriverWait(self.driver, 8).until(
                    EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, 'iframe[id*="sp_message"]'))
                )
                print("   ✅ Iframe encontrado! Entrando...")
                
                try:
                    accept_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[title*="Accept"]'))
                    )
                    accept_button.click()
                    print("   ✅ Botão Accept clicado!")
                except:
                    try:
                        accept_button = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]"))
                        )
                        accept_button.click()
                        print("   ✅ Botão Accept clicado via XPath!")
                    except:
                        print("   ⚠️ Nenhum botão Accept encontrado")
                
                self.driver.switch_to.default_content()
                print("   🏠 Voltou para conteúdo principal")
                time.sleep(2)
                
            except:
                print("   ℹ️ Nenhum iframe de popup encontrado")
            
            return True
            
        except Exception as e:
            print(f"   ⚠️ Erro ao tratar popup: {e}")
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return True
    
    def clean_text_data(self, text):
        """Limpa e padroniza dados de texto"""
        if not text:
            return ""
        
        cleaned = str(text).strip()
        empty_values = ['', '-', 'N/A', 'n/a', 'NA', 'na', '?', 'null', 'None', 'undefined']
        
        if cleaned.lower() in [v.lower() for v in empty_values]:
            return ""
        
        return cleaned
    
    def parse_market_value(self, value_text):
        """Converte valor de mercado para formato numérico"""
        try:
            if not value_text or value_text in ['-', 'N/A', '', '?', 'null']:
                return 0
            
            value_clean = str(value_text).replace('€', '').replace(',', '.').replace(' ', '').strip()
            value_clean = re.sub(r'[^\d.,kmKM]', '', value_clean)
            
            if not value_clean:
                return 0
            
            value_clean = value_clean.lower()
            
            if 'm' in value_clean:
                value_clean = value_clean.replace('m', '')
                try:
                    return float(value_clean) * 1000000
                except:
                    return 0
            elif 'k' in value_clean:
                value_clean = value_clean.replace('k', '')
                try:
                    return float(value_clean) * 1000
                except:
                    return 0
            else:
                try:
                    return float(value_clean)
                except:
                    return 0
        except Exception as e:
            print(f"   ⚠️ Erro ao converter valor '{value_text}': {e}")
            return 0
    
    def parse_birth_date_and_age(self, text):
        """Extrai data de nascimento e idade - SOLUÇÃO DEFINITIVA"""
        try:
            if not text:
                return "", None
            
            text = str(text).strip()
            
            
            # Padrão: "08/02/2002 (20)" -> "08/02/2002" e 20
            if '(' in text and ')' in text:
                # Dividir pelo '('
                parts = text.split('(')
                if len(parts) == 2:
                    birth_date = parts[0].strip()  # "08/02/2002"
                    age_part = parts[1].replace(')', '').strip()  # "20"
                    
                    try:
                        age = int(age_part)
                        return birth_date, age
                    except ValueError:
                        print(f"   ⚠️ Idade inválida: '{age_part}'")  
                        return birth_date, None
            
            # Se não tem parênteses, retorna como está
            print(f"   ⚠️ Sem padrão reconhecido: '{text}'") 
            return text, None
            
        except Exception as e:
            print(f"   ❌ Erro ao processar '{text}': {e}")
            return text, None
    
    def extract_nationality(self, nat_cell):
        """Extrai nacionalidade das bandeiras - PADRONIZADO"""
        try:
            flag_imgs = nat_cell.find_elements(By.CSS_SELECTOR, "img[title]")
            nationalities = []
            
            # Lista expandida de países
            country_keywords = [
                'Brazil', 'Argentina', 'Uruguay', 'Paraguay', 'Colombia', 'Chile', 
                'Peru', 'Ecuador', 'Venezuela', 'Bolivia', 'Spain', 'Italy', 
                'France', 'Germany', 'Portugal', 'England', 'Netherlands', 
                'Belgium', 'Croatia', 'Serbia', 'Poland', 'United States', 
                'Mexico', 'Japan', 'South Korea', 'Australia', 'Canada',
                'Nigeria', 'Ghana', 'Senegal', 'Morocco', 'Algeria', 'Tunisia',
                'Cameroon', 'Ivory Coast', 'Mali', 'Burkina Faso'
            ]
            
            for img in flag_imgs:
                title = img.get_attribute("title")
                if title and title.strip():
                    if any(country in title for country in country_keywords):
                        nationalities.append(title.strip())
            
            return " / ".join(nationalities) if nationalities else ""
            
        except Exception as e:
            print(f"   ⚠️ Erro ao extrair nacionalidade: {e}")
            return ""

class TransfermarktScraper2025(TransfermarktBase):
    """Scraper específico para layout 2025 (com campo contrato) - ATUALIZADO"""
    
    def __init__(self):
        super().__init__()
        self.layout_name = "Layout 2025"
    
    def find_squad_table(self):
        """Encontra a tabela de elenco específica para 2025"""
        table_selectors = [
            "table.items",
            ".responsive-table table",
            "table[class*='items']",
            ".items tbody",
            "table tbody"
        ]
        
        for selector in table_selectors:
            try:
                table = self.driver.find_element(By.CSS_SELECTOR, selector)
                print(f"   ✅ Tabela 2025 encontrada com: {selector}")
                return table
            except:
                continue
        
        print("   ❌ Nenhuma tabela 2025 encontrada")
        return None
    
    def extract_player_name_and_position(self, name_cell):
        """Extrai nome e posição específico para layout 2025"""
        try:
            player_name = ""
            player_link = ""
            position = ""
            
            # Estratégias específicas para 2025
            try:
                # Método 1: Link direto do jogador
                name_link = name_cell.find_element(By.CSS_SELECTOR, "a[href*='/profil/spieler/']")
                player_name = self.clean_text_data(name_link.text)
                player_link = name_link.get_attribute('href')
            except:
                try:
                    # Método 2: Qualquer link
                    name_link = name_cell.find_element(By.TAG_NAME, "a")
                    player_name = self.clean_text_data(name_link.text)
                    player_link = name_link.get_attribute('href')
                except:
                    # Método 3: Texto direto
                    player_name = self.clean_text_data(name_cell.text)
            
            # Extrair posição - métodos específicos para 2025
            try:
                # Método 1: Estrutura inline-table
                inline_table = name_cell.find_element(By.CLASS_NAME, "inline-table")
                position_cell = inline_table.find_element(By.XPATH, ".//tr[2]/td")
                position = self.clean_text_data(position_cell.text)
            except:
                try:
                    # Método 2: Buscar por texto pequeno abaixo do nome
                    small_elements = name_cell.find_elements(By.TAG_NAME, "small")
                    for small in small_elements:
                        text = self.clean_text_data(small.text)
                        if text and len(text) <= 20:  # Posições são textos curtos
                            position = text
                            break
                except:
                    position = ""
            
            # Limpar nome
            if player_name:
                player_name = re.sub(r'[^\w\s\-áàâãéèêíìîóòôõúùûçÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛÇ]', '', player_name)
                player_name = player_name.strip()
            
            return player_name, player_link, position
            
        except Exception as e:
            print(f"   ⚠️ Erro ao extrair nome/posição 2025: {e}")
            return "", "", ""
    
    def extract_player_data(self, row):
        """Extrai dados completos do jogador para layout 2025 - MAPEAMENTO CORRIGIDO"""
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            
            if len(cells) < 10:  # 2025 tem pelo menos 10 colunas
                return None
            
            player_data = {}
            
            
            
            
            # 1. Número da camisa (célula 0)
            try:
                number_div = cells[0].find_element(By.CSS_SELECTOR, ".rn_nummer")
                numero = number_div.text.strip()
                if not numero or not numero.isdigit():
                    return None
                player_data['numero_camisa'] = numero
            except:
                return None
            
            # 2. Nome e posição (célula 1)
            player_name, player_link, position = self.extract_player_name_and_position(cells[1])
            
            if not player_name or len(player_name) < 2:
                return None
            
            player_data['nome'] = player_name
            player_data['link_perfil'] = player_link
            player_data['posicao'] = position
            
            # 3. Data de nascimento e idade - CORRIGIR ÍNDICE
            try:
                # Tentar diferentes células até encontrar a correta
                birth_text = ""
                for idx in [2, 3, 4, 5]:
                    try:
                        test_text = self.clean_text_data(cells[idx].text)
                        # Verificar se parece com data de nascimento
                        if '(' in test_text and ')' in test_text and ('/' in test_text or '-' in test_text):
                            birth_text = test_text
    
                            break
                    except:
                        continue
                
                if birth_text:
                    birth_date, age = self.parse_birth_date_and_age(birth_text)
                    player_data['data_nascimento'] = birth_date
                    player_data['idade'] = age
                else:
                    player_data['data_nascimento'] = ""
                    player_data['idade'] = None
                    print("   ⚠️ Data de nascimento não encontrada")
                    
            except Exception as e:
                print(f"   ❌ Erro ao extrair data: {e}")
                player_data['data_nascimento'] = ""
                player_data['idade'] = None
            
            # 4. Nacionalidade - CORRIGIR ÍNDICE
            try:
                # Tentar diferentes células até encontrar bandeiras
                nacionalidade = ""
                for idx in [3, 4, 5, 6]:
                    try:
                        test_nat = self.extract_nationality(cells[idx])
                        if test_nat:
                            nacionalidade = test_nat
                            
                            break
                    except:
                        continue
                
                player_data['nacionalidade'] = nacionalidade
                
            except Exception as e:
                print(f"   ❌ Erro ao extrair nacionalidade: {e}")
                player_data['nacionalidade'] = ""
            
            # 5. Altura - CORRIGIR ÍNDICE
            try:
                # Procurar por padrão de altura (ex: "1,80 m", "180 cm")
                altura = ""
                for idx in range(4, 8):
                    try:
                        test_text = self.clean_text_data(cells[idx].text)
                        # Verificar se parece com altura
                        if re.search(r'\d[,\.]\d+\s*m|\d+\s*cm', test_text):
                            altura = test_text
                            break
                    except:
                        continue
                
                player_data['altura'] = altura
                
            except Exception as e:
                print(f"   ❌ Erro ao extrair altura: {e}")
                player_data['altura'] = ""
            
            # 6. Pé preferido - CORRIGIR ÍNDICE
            try:
                # Procurar por "left", "right", "both", "esquerdo", "direito"
                pe_preferido = ""
                for idx in range(5, 9):
                    try:
                        test_text = self.clean_text_data(cells[idx].text).lower()
                        if any(word in test_text for word in ['left', 'right', 'both', 'esquerdo', 'direito', 'ambos']):
                            pe_preferido = cells[idx].text.strip()
                            break
                    except:
                        continue
                
                player_data['pe_preferido'] = pe_preferido
                
            except Exception as e:
                print(f"   ❌ Erro ao extrair pé preferido: {e}")
                player_data['pe_preferido'] = ""
            
            # 7. Data de entrada - CORRIGIR ÍNDICE
            try:
                # Procurar por padrão de data (sem parênteses)
                data_entrada = ""
                for idx in range(6, 10):
                    try:
                        test_text = self.clean_text_data(cells[idx].text)
                        # Verificar se parece com data simples
                        if re.search(r'\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2}', test_text) and '(' not in test_text:
                            data_entrada = test_text
                            
                            break
                    except:
                        continue
                
                player_data['data_entrada'] = data_entrada
                
            except Exception as e:
                print(f"   ❌ Erro ao extrair data entrada: {e}")
                player_data['data_entrada'] = ""
            
            # 8. Clube de origem - CORREÇÃO ESPECÍFICA
            try:
                # Procurar por links de clubes nas células corretas
                clube_origem = ""
                
                # Para layout 2025, o clube de origem geralmente está na célula 10
                # Vamos verificar células 10, 9, 8 em ordem
                for idx in [10, 9, 8]:
                    try:
                        cell = cells[idx]
                        
                        # Primeiro tentar encontrar link de clube
                        try:
                            club_link = cell.find_element(By.TAG_NAME, "a")
                            club_title = club_link.get_attribute("title")
                            
                            if club_title and club_title.strip():
                                # Limpar informações extras do title
                                if ":" in club_title:
                                    club_title = club_title.split(":")[0]
                                
                                # Verificar se não é altura, data ou outros dados
                                if not re.search(r'\d+[,\.]\d+\s*m|\d+\s*cm|\d{2}/\d{2}/\d{4}|left|right', club_title.lower()):
                                    clube_origem = club_title.strip()
                                
                                    break
                                    
                        except:
                            # Se não tem link, tentar texto direto
                            text = cell.text.strip()
                            
                            # Verificar se o texto parece com nome de clube
                            if (text and len(text) > 2 and 
                                text not in ['-', 'N/A', '?', ''] and
                                not re.search(r'\d+[,\.]\d+\s*m|\d+\s*cm|\d{2}/\d{2}/\d{4}|left|right|202\d', text.lower())):
                                
                                clube_origem = text
                                break
                                
                    except:
                        continue
                
                player_data['clube_origem'] = clube_origem
                
            except Exception as e:
                print(f"   ❌ Erro ao extrair clube origem: {e}")
                player_data['clube_origem'] = ""
                            
            except Exception as e:
                print(f"   ❌ Erro ao extrair clube origem: {e}")
                player_data['clube_origem'] = ""
            
            # 9. Contrato (específico do layout 2025) - MELHORADO
            try:
                # Procurar por data de contrato (geralmente célula 11, às vezes 9)
                contrato = ""
                
                for idx in [11, 9]:
                    try:
                        test_text = self.clean_text_data(cells[idx].text)
                        
                        # Verificar se parece com data de contrato (ano futuro)
                        if re.search(r'202[5-9]|203\d', test_text) and '/' in test_text:
                            contrato = test_text
                            break
                            
                    except:
                        continue
                
                player_data['contrato_ate'] = contrato
                
            except Exception as e:
                print(f"   ❌ Erro ao extrair contrato: {e}")
                player_data['contrato_ate'] = ""
            
            # 10. Clube atual (será preenchido depois)
            player_data['clube_atual'] = ""
            
            # 11. Valor de mercado (última célula ou procurar por €)
            try:
                valor_texto = ""
                valor_numerico = 0
                
                # Procurar por valor com €
                for idx in range(len(cells)-3, len(cells)):
                    try:
                        cell = cells[idx]
                        try:
                            value_link = cell.find_element(By.TAG_NAME, "a")
                            value_text = value_link.text.strip()
                        except:
                            value_text = cell.text.strip()
                        
                        if '€' in value_text or 'k' in value_text.lower() or 'm' in value_text.lower():
                            valor_texto = value_text
                            valor_numerico = self.parse_market_value(value_text)
                            break
                    except:
                        continue
                
                player_data['valor_mercado_texto'] = valor_texto
                player_data['valor_mercado_numerico'] = valor_numerico
                
            except Exception as e:
                print(f"   ❌ Erro ao extrair valor: {e}")
                player_data['valor_mercado_texto'] = ""
                player_data['valor_mercado_numerico'] = 0
            
            return player_data
            
        except Exception as e:
            print(f"   ⚠️ Erro ao extrair dados 2025: {e}")
            return None
    
    def scrape_team_players(self, team_name, team_url, season):
        """Coleta dados específica para layout 2025"""
        print(f"\n🏈 Coletando {team_name} - {season} (Layout 2025)")
        
        try:
            self.driver.get(team_url)
            self.handle_iframe_popup()
            time.sleep(5)
            
            squad_table = self.find_squad_table()
            if not squad_table:
                return []
            
            players_data = []
            rows = squad_table.find_elements(By.TAG_NAME, "tr")
            
            print(f"   📊 Processando {len(rows)} linhas (Layout 2025)...")
            
            valid_players = 0
            for i, row in enumerate(rows):
                try:
                    player_data = self.extract_player_data(row)
                    
                    if player_data and player_data.get('nome'):
                        player_data['clube'] = team_name
                        player_data['clube_atual'] = team_name  # NOVO: clube atual é o time atual
                        player_data['temporada'] = season
                        player_data['layout_type'] = "2025"  # NOVO: identificador do layout
                        player_data['data_coleta'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        players_data.append(player_data)
                        valid_players += 1
                        
                        if valid_players == 1:
                            print(f"   ✅ Primeiro jogador 2025: {player_data['nome']} - Nacionalidade: {player_data.get('nacionalidade', 'N/A')}")
                    
                except Exception as e:
                    continue
            
            print(f"   ✅ {len(players_data)} jogadores coletados (Layout 2025)")
            return players_data
            
        except Exception as e:
            print(f"❌ Erro ao acessar {team_name} (Layout 2025): {e}")
            return []

class TransfermarktScraperLegacy(TransfermarktBase):
    """Scraper específico para layout legacy (2020-2024) - COLUNAS PADRONIZADAS"""
    
    def __init__(self):
        super().__init__()
        self.layout_name = "Layout Legacy"
    
    def find_squad_table(self):
        """Encontra a tabela de elenco específica para legacy"""
        try:
            table = self.driver.find_element(By.CSS_SELECTOR, "table.items")
            print(f"   ✅ Tabela Legacy encontrada: table.items")
            return table
        except:
            print("   ❌ Nenhuma tabela Legacy encontrada")
            return None
    
    def extract_player_number(self, row):
        """Extrai número da camisa da div.rn_nummer"""
        try:
            number_div = row.find_element(By.CSS_SELECTOR, ".rn_nummer")
            number = number_div.text.strip()
            
            if number.isdigit():
                return number
            
            return None
        except:
            return None
    
    def extract_player_name_and_info(self, row):
        """Extrai nome, posição e link do jogador da estrutura inline-table"""
        try:
            # Procurar pela tabela inline-table na segunda célula
            inline_table = row.find_element(By.CSS_SELECTOR, "td.posrela .inline-table")
            
            player_name = ""
            player_link = ""
            position = ""
            
            # Nome e link estão na primeira linha da inline-table
            try:
                name_link = inline_table.find_element(By.CSS_SELECTOR, "tr:first-child td.hauptlink a")
                player_name = name_link.text.strip()
                player_link = name_link.get_attribute('href')
                
                # Remover ícones de lesão ou capitão do nome
                icon_spans = name_link.find_elements(By.CSS_SELECTOR, "span.verletzt-table, span.kapitaenicon-table, span.ausfall-1-table")
                for span in icon_spans:
                    icon_text = span.text
                    if icon_text in player_name:
                        player_name = player_name.replace(icon_text, "").strip()
                
            except Exception as e:
                print(f"   ⚠️ Erro ao extrair nome: {e}")
                return None, None, None
            
            # Posição está na segunda linha da inline-table
            try:
                position_cell = inline_table.find_element(By.CSS_SELECTOR, "tr:last-child td")
                position = position_cell.text.strip()
            except:
                position = ""
            
            # Limpar nome
            if player_name:
                # Remover caracteres especiais mas manter acentos
                player_name = re.sub(r'[^\w\s\-áàâãéèêíìîóòôõúùûçÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛÇ]', '', player_name)
                player_name = player_name.strip()
            
            return player_name, position, player_link
            
        except Exception as e:
            print(f"   ⚠️ Erro ao extrair info do jogador: {e}")
            return None, None, None
    
    def extract_player_data(self, row):
        """Extrai dados completos do jogador - COLUNAS PADRONIZADAS"""
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            
            if len(cells) < 10:  # Mínimo necessário
                return None
            
            player_data = {}
            
            # 1. Número da camisa (célula 0)
            numero = self.extract_player_number(row)
            if not numero:
                return None
            player_data['numero_camisa'] = numero
            
            # 2. Nome, posição e link (célula 1)
            nome, posicao, link = self.extract_player_name_and_info(row)
            if not nome:
                return None
            
            player_data['nome'] = nome
            player_data['posicao'] = posicao or ""
            player_data['link_perfil'] = link or ""
            
            # 3. Data nascimento/idade (célula 5) - CORRIGIDO
            try:
                birth_text = self.clean_text_data(cells[5].text)
                birth_date, age = self.parse_birth_date_and_age(birth_text)
                player_data['data_nascimento'] = birth_date
                player_data['idade'] = age
            except:
                player_data['data_nascimento'] = ""
                player_data['idade'] = None
            
            # 4. Nacionalidade (célula 6) - PADRONIZADO
            try:
                player_data['nacionalidade'] = self.extract_nationality(cells[6])
            except:
                player_data['nacionalidade'] = ""
            
            # 5. Clube atual (célula 7) - MANTIDO
            try:
                club_cell = cells[7]
                try:
                    club_link = club_cell.find_element(By.TAG_NAME, "a")
                    club_title = club_link.get_attribute("title")
                    if club_title and club_title.strip():
                        # Remover data se existir
                        if "(" in club_title:
                            club_title = club_title.split("(")[0].strip()
                        player_data['clube_atual'] = club_title.strip()
                    else:
                        club_text = club_cell.text.strip()
                        if "(" in club_text:
                            club_text = club_text.split("(")[0].strip()
                        player_data['clube_atual'] = club_text
                except:
                    club_text = club_cell.text.strip()
                    if "(" in club_text:
                        club_text = club_text.split("(")[0].strip()
                    player_data['clube_atual'] = club_text
            except:
                player_data['clube_atual'] = ""
            
            # 6. Altura (célula 8)
            try:
                height_cell = cells[8]
                player_data['altura'] = height_cell.text.strip()
            except:
                player_data['altura'] = ""
            
            # 7. Pé preferido (célula 9)
            try:
                foot_cell = cells[9]
                player_data['pe_preferido'] = foot_cell.text.strip()
            except:
                player_data['pe_preferido'] = ""
            
            # 8. Data de entrada (célula 10)
            try:
                joined_cell = cells[10]
                player_data['data_entrada'] = joined_cell.text.strip()
            except:
                player_data['data_entrada'] = ""
            
            # 9. Clube de origem (célula 11)
            try:
                from_cell = cells[11]
                try:
                    club_link = from_cell.find_element(By.TAG_NAME, "a")
                    club_title = club_link.get_attribute("title")
                    if club_title and club_title.strip():
                        # Remover informações de transferência (ex: ": Ablöse €500k")
                        if ":" in club_title:
                            club_title = club_title.split(":")[0]
                        player_data['clube_origem'] = club_title.strip()
                    else:
                        player_data['clube_origem'] = from_cell.text.strip()
                except:
                    text = from_cell.text.strip()
                    if text and text not in ["&nbsp;", "-", ""]:
                        player_data['clube_origem'] = text
                    else:
                        player_data['clube_origem'] = ""
            except:
                player_data['clube_origem'] = ""
            
            # 10. Contrato até - NOVO (sempre vazio para layout legacy)
            player_data['contrato_ate'] = ""
            
            # 11. Valor de mercado (célula 12)
            try:
                value_cell = cells[12]
                try:
                    value_link = value_cell.find_element(By.TAG_NAME, "a")
                    value_text = value_link.text.strip()
                except:
                    value_text = value_cell.text.strip()
                
                if value_text and value_text not in ['-', 'N/A', '?', '&nbsp;', '']:
                    player_data['valor_mercado_texto'] = value_text
                    player_data['valor_mercado_numerico'] = self.parse_market_value(value_text)
                else:
                    player_data['valor_mercado_texto'] = ""
                    player_data['valor_mercado_numerico'] = 0
            except:
                player_data['valor_mercado_texto'] = ""
                player_data['valor_mercado_numerico'] = 0
            
            return player_data
            
        except Exception as e:
            print(f"   ⚠️ Erro ao extrair dados do jogador: {e}")
            return None
    
    def scrape_team_players(self, team_name, team_url, season):
        """Coleta dados dos jogadores de um time"""
        print(f"\n🏈 Coletando {team_name} - {season} (Layout Legacy)")
        
        try:
            self.driver.get(team_url)
            self.handle_iframe_popup()
            time.sleep(5)
            
            # Procurar tabela com classe "items"
            squad_table = self.find_squad_table()
            if not squad_table:
                return []
            
            players_data = []
            tbody = squad_table.find_element(By.TAG_NAME, "tbody")
            rows = tbody.find_elements(By.TAG_NAME, "tr")
            
            print(f"   📊 Processando {len(rows)} linhas...")
            
            valid_players = 0
            
            for i, row in enumerate(rows):
                try:
                    player_data = self.extract_player_data(row)
                    
                    if player_data and player_data.get('nome'):
                        player_data['clube'] = team_name
                        player_data['temporada'] = season
                        player_data['layout_type'] = "2025"  # NOVO: todos como 2025
                        player_data['data_coleta'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        players_data.append(player_data)
                        valid_players += 1
                        
                        if valid_players == 1:
                            print(f"   ✅ Primeiro jogador Legacy: {player_data['nome']} - Nacionalidade: {player_data.get('nacionalidade', 'N/A')}")
                    
                except Exception as e:
                    continue
            
            print(f"   ✅ {len(players_data)} jogadores coletados (Layout Legacy)")
            return players_data
            
        except Exception as e:
            print(f"❌ Erro ao acessar {team_name}: {e}")
            return []

class TransfermarktJogadores:
    """Classe principal que gerencia os scrapers específicos - ATUALIZADA"""
    
    def __init__(self):
        self.default_save_path = r"C:\Users\migue\trabalho\análise de dados\selenium\talentos jovens\Data"
        
        # Times por temporada com URLs do Transfermarkt
        self.times_por_temporada = {
            "2025": {
                "Palmeiras": "https://www.transfermarkt.com/se-palmeiras-sao-paulo/kader/verein/1023/saison_id/2024/plus/1",
                "Botafogo": "https://www.transfermarkt.com/botafogo-rio-de-janeiro/kader/verein/537/saison_id/2024/plus/1",
                "Fortaleza": "https://www.transfermarkt.com/fortaleza-esporte-clube/kader/verein/10870/saison_id/2024/plus/1",
                "Flamengo": "https://www.transfermarkt.com/flamengo-rio-de-janeiro/kader/verein/614/saison_id/2024/plus/1",
                "São Paulo": "https://www.transfermarkt.com/fc-sao-paulo/kader/verein/585/saison_id/2024/plus/1",
                "Bahia": "https://www.transfermarkt.com/esporte-clube-bahia/kader/verein/10010/saison_id/2024/plus/1",
                "Cruzeiro": "https://www.transfermarkt.com/ec-cruzeiro-belo-horizonte/kader/verein/609/saison_id/2024/plus/1",
                "Vasco da Gama": "https://www.transfermarkt.com/vasco-da-gama-rio-de-janeiro/kader/verein/978/saison_id/2024/plus/1",
                "Atlético-MG": "https://www.transfermarkt.com/clube-atletico-mineiro/kader/verein/330/saison_id/2024/plus/1",
                "Internacional": "https://www.transfermarkt.com/sc-internacional-porto-alegre/kader/verein/6600/saison_id/2024/plus/1",
                "Bragantino": "https://www.transfermarkt.com/red-bull-bragantino/kader/verein/8793/saison_id/2024/plus/1",
                "Juventude": "https://www.transfermarkt.com/esporte-clube-juventude/kader/verein/10492/saison_id/2024/plus/1",
                "Grêmio": "https://www.transfermarkt.com/gremio-porto-alegre/kader/verein/210/saison_id/2024/plus/1",
                "Fluminense": "https://www.transfermarkt.com/fluminense-rio-de-janeiro/kader/verein/2462/saison_id/2024/plus/1",
                "Corinthians": "https://www.transfermarkt.com/corinthians-sao-paulo/kader/verein/199/saison_id/2024/plus/1",
                "Vitória": "https://www.transfermarkt.com/esporte-clube-vitoria/kader/verein/2125/saison_id/2024/plus/1",
                "Santos": "https://www.transfermarkt.com/fc-santos/kader/verein/221/saison_id/2024/plus/1",
                "Ceará": "https://www.transfermarkt.com/ceara-sporting-club/kader/verein/2029/saison_id/2024/plus/1",
                "Mirassol": "https://www.transfermarkt.com/mirassol-futebol-clube-sp-/kader/verein/3876/saison_id/2024/plus/1",
                "Sport": "https://www.transfermarkt.com/sport-club-do-recife/kader/verein/8718/saison_id/2024/plus/1"
            },
            "2024": {
                "Palmeiras": "https://www.transfermarkt.com/se-palmeiras-sao-paulo/kader/verein/1023/saison_id/2023/plus/1",
                "Botafogo": "https://www.transfermarkt.com/botafogo-rio-de-janeiro/kader/verein/537/saison_id/2023/plus/1",
                "Fortaleza": "https://www.transfermarkt.com/fortaleza-esporte-clube/kader/verein/10870/saison_id/2023/plus/1",
                "Flamengo": "https://www.transfermarkt.com/flamengo-rio-de-janeiro/kader/verein/614/saison_id/2023/plus/1",
                "São Paulo": "https://www.transfermarkt.com/fc-sao-paulo/kader/verein/585/saison_id/2023/plus/1",
                "Bahia": "https://www.transfermarkt.com/esporte-clube-bahia/kader/verein/10010/saison_id/2023/plus/1",
                "Cruzeiro": "https://www.transfermarkt.com/ec-cruzeiro-belo-horizonte/kader/verein/609/saison_id/2023/plus/1",
                "Vasco da Gama": "https://www.transfermarkt.com/vasco-da-gama-rio-de-janeiro/kader/verein/978/saison_id/2023/plus/1",
                "Atlético-MG": "https://www.transfermarkt.com/clube-atletico-mineiro/kader/verein/330/saison_id/2023/plus/1",
                "Internacional": "https://www.transfermarkt.com/sc-internacional-porto-alegre/kader/verein/6600/saison_id/2023/plus/1",
                "Bragantino": "https://www.transfermarkt.com/red-bull-bragantino/kader/verein/8793/saison_id/2023/plus/1",
                "Juventude": "https://www.transfermarkt.com/esporte-clube-juventude/kader/verein/10492/saison_id/2023/plus/1",
                "Criciúma": "https://www.transfermarkt.com/criciuma-esporte-clube/kader/verein/7178/saison_id/2023/plus/1",
                "Athletico-PR": "https://www.transfermarkt.com/club-athletico-paranaense/kader/verein/679/saison_id/2023/plus/1",
                "Grêmio": "https://www.transfermarkt.com/gremio-porto-alegre/kader/verein/210/saison_id/2023/plus/1",
                "Fluminense": "https://www.transfermarkt.com/fluminense-rio-de-janeiro/kader/verein/2462/saison_id/2023/plus/1",
                "Corinthians": "https://www.transfermarkt.com/corinthians-sao-paulo/kader/verein/199/saison_id/2023/plus/1",
                "Vitória": "https://www.transfermarkt.com/esporte-clube-vitoria/kader/verein/2125/saison_id/2023/plus/1",
                "Cuiabá": "https://www.transfermarkt.com/cuiaba-ec-mt-/kader/verein/28022/saison_id/2023/plus/1",
                "Atlético-GO": "https://www.transfermarkt.com/atletico-clube-goianiense/kader/verein/15172/saison_id/2023/plus/1"
            },
            "2023": {
                "Palmeiras": "https://www.transfermarkt.com/se-palmeiras-sao-paulo/kader/verein/1023/saison_id/2022/plus/1",
                "Grêmio": "https://www.transfermarkt.com/gremio-porto-alegre/kader/verein/210/saison_id/2022/plus/1",
                "Flamengo": "https://www.transfermarkt.com/flamengo-rio-de-janeiro/kader/verein/614/saison_id/2022/plus/1",
                "Atlético-MG": "https://www.transfermarkt.com/clube-atletico-mineiro/kader/verein/330/saison_id/2022/plus/1",
                "Botafogo": "https://www.transfermarkt.com/botafogo-rio-de-janeiro/kader/verein/537/saison_id/2022/plus/1",
                "Bragantino": "https://www.transfermarkt.com/red-bull-bragantino/kader/verein/8793/saison_id/2022/plus/1",
                "Fluminense": "https://www.transfermarkt.com/fluminense-rio-de-janeiro/kader/verein/2462/saison_id/2022/plus/1",
                "Internacional": "https://www.transfermarkt.com/sc-internacional-porto-alegre/kader/verein/6600/saison_id/2022/plus/1",
                "Fortaleza": "https://www.transfermarkt.com/fortaleza-esporte-clube/kader/verein/10870/saison_id/2022/plus/1",
                "São Paulo": "https://www.transfermarkt.com/fc-sao-paulo/kader/verein/585/saison_id/2022/plus/1",
                "Cuiabá": "https://www.transfermarkt.com/cuiaba-ec-mt-/kader/verein/28022/saison_id/2022/plus/1",
                "Corinthians": "https://www.transfermarkt.com/corinthians-sao-paulo/kader/verein/199/saison_id/2022/plus/1",
                "Athletico-PR": "https://www.transfermarkt.com/club-athletico-paranaense/kader/verein/679/saison_id/2022/plus/1",
                "Bahia": "https://www.transfermarkt.com/esporte-clube-bahia/kader/verein/10010/saison_id/2022/plus/1",
                "Santos": "https://www.transfermarkt.com/fc-santos/kader/verein/221/saison_id/2022/plus/1",
                "Goiás": "https://www.transfermarkt.com/goias-ec/kader/verein/3197/saison_id/2022/plus/1",
                "Vasco da Gama": "https://www.transfermarkt.com/vasco-da-gama-rio-de-janeiro/kader/verein/978/saison_id/2022/plus/1",
                "Coritiba": "https://www.transfermarkt.com/coritiba-fc/kader/verein/776/saison_id/2022/plus/1",
                "América-MG": "https://www.transfermarkt.com/america-futebol-clube-mg-/kader/verein/2863/saison_id/2022/plus/1",
                "Cruzeiro": "https://www.transfermarkt.com/ec-cruzeiro-belo-horizonte/kader/verein/609/saison_id/2022/plus/1"
            },
            "2022": {
                "Palmeiras": "https://www.transfermarkt.com/se-palmeiras-sao-paulo/kader/verein/1023/saison_id/2021/plus/1",
                "Internacional": "https://www.transfermarkt.com/sc-internacional-porto-alegre/kader/verein/6600/saison_id/2021/plus/1",
                "Fluminense": "https://www.transfermarkt.com/fluminense-rio-de-janeiro/kader/verein/2462/saison_id/2021/plus/1",
                "Corinthians": "https://www.transfermarkt.com/corinthians-sao-paulo/kader/verein/199/saison_id/2021/plus/1",
                "Flamengo": "https://www.transfermarkt.com/flamengo-rio-de-janeiro/kader/verein/614/saison_id/2021/plus/1",
                "Athletico-PR": "https://www.transfermarkt.com/club-athletico-paranaense/kader/verein/679/saison_id/2021/plus/1",
                "Atlético-MG": "https://www.transfermarkt.com/clube-atletico-mineiro/kader/verein/330/saison_id/2021/plus/1",
                "Fortaleza": "https://www.transfermarkt.com/fortaleza-esporte-clube/kader/verein/10870/saison_id/2021/plus/1",
                "São Paulo": "https://www.transfermarkt.com/fc-sao-paulo/kader/verein/585/saison_id/2021/plus/1",
                "América-MG": "https://www.transfermarkt.com/america-futebol-clube-mg-/kader/verein/2863/saison_id/2021/plus/1",
                "Botafogo": "https://www.transfermarkt.com/botafogo-rio-de-janeiro/kader/verein/537/saison_id/2021/plus/1",
                "Santos": "https://www.transfermarkt.com/fc-santos/kader/verein/221/saison_id/2021/plus/1",
                "Goiás": "https://www.transfermarkt.com/goias-ec/kader/verein/3197/saison_id/2021/plus/1",
                "Bragantino": "https://www.transfermarkt.com/red-bull-bragantino/kader/verein/8793/saison_id/2021/plus/1",
                "Coritiba": "https://www.transfermarkt.com/coritiba-fc/kader/verein/776/saison_id/2021/plus/1",
                "Cuiabá": "https://www.transfermarkt.com/cuiaba-ec-mt-/kader/verein/28022/saison_id/2021/plus/1",
                "Ceará": "https://www.transfermarkt.com/ceara-sporting-club/kader/verein/2029/saison_id/2021/plus/1",
                "Atlético-GO": "https://www.transfermarkt.com/atletico-clube-goianiense/kader/verein/15172/saison_id/2021/plus/1",
                "Avaí": "https://www.transfermarkt.com/avai-fc-sc-/kader/verein/2035/saison_id/2021/plus/1",
                "Juventude": "https://www.transfermarkt.com/esporte-clube-juventude/kader/verein/10492/saison_id/2021/plus/1"
            },
            "2021": {
                "Atlético-MG": "https://www.transfermarkt.com/clube-atletico-mineiro/kader/verein/330/saison_id/2020/plus/1",
                "Flamengo": "https://www.transfermarkt.com/flamengo-rio-de-janeiro/kader/verein/614/saison_id/2020/plus/1",
                "Palmeiras": "https://www.transfermarkt.com/se-palmeiras-sao-paulo/kader/verein/1023/saison_id/2020/plus/1",
                "Fortaleza": "https://www.transfermarkt.com/fortaleza-esporte-clube/kader/verein/10870/saison_id/2020/plus/1",
                "Corinthians": "https://www.transfermarkt.com/corinthians-sao-paulo/kader/verein/199/saison_id/2020/plus/1",
                "Bragantino": "https://www.transfermarkt.com/red-bull-bragantino/kader/verein/8793/saison_id/2020/plus/1",
                "Fluminense": "https://www.transfermarkt.com/fluminense-rio-de-janeiro/kader/verein/2462/saison_id/2020/plus/1",
                "América-MG": "https://www.transfermarkt.com/america-futebol-clube-mg-/kader/verein/2863/saison_id/2020/plus/1",
                "Atlético-GO": "https://www.transfermarkt.com/atletico-clube-goianiense/kader/verein/15172/saison_id/2020/plus/1",
                "Santos": "https://www.transfermarkt.com/fc-santos/kader/verein/221/saison_id/2020/plus/1",
                "Ceará": "https://www.transfermarkt.com/ceara-sporting-club/kader/verein/2029/saison_id/2020/plus/1",
                "Internacional": "https://www.transfermarkt.com/sc-internacional-porto-alegre/kader/verein/6600/saison_id/2020/plus/1",
                "São Paulo": "https://www.transfermarkt.com/fc-sao-paulo/kader/verein/585/saison_id/2020/plus/1",
                "Athletico-PR": "https://www.transfermarkt.com/club-athletico-paranaense/kader/verein/679/saison_id/2020/plus/1",
                "Cuiabá": "https://www.transfermarkt.com/cuiaba-ec-mt-/kader/verein/28022/saison_id/2020/plus/1",
                "Juventude": "https://www.transfermarkt.com/esporte-clube-juventude/kader/verein/10492/saison_id/2020/plus/1",
                "Grêmio": "https://www.transfermarkt.com/gremio-porto-alegre/kader/verein/210/saison_id/2020/plus/1",
                "Bahia": "https://www.transfermarkt.com/esporte-clube-bahia/kader/verein/10010/saison_id/2020/plus/1",
                "Sport": "https://www.transfermarkt.com/sport-club-do-recife/kader/verein/8718/saison_id/2020/plus/1",
                "Chapecoense": "https://www.transfermarkt.com/chapecoense/kader/verein/17776/saison_id/2020/plus/1"
            },
            "2020": {
                "Flamengo": "https://www.transfermarkt.com/flamengo-rio-de-janeiro/kader/verein/614/saison_id/2019/plus/1",
                "Internacional": "https://www.transfermarkt.com/sc-internacional-porto-alegre/kader/verein/6600/saison_id/2019/plus/1",
                "Atlético-MG": "https://www.transfermarkt.com/clube-atletico-mineiro/kader/verein/330/saison_id/2019/plus/1",
                "São Paulo": "https://www.transfermarkt.com/fc-sao-paulo/kader/verein/585/saison_id/2019/plus/1",
                "Fluminense": "https://www.transfermarkt.com/fluminense-rio-de-janeiro/kader/verein/2462/saison_id/2019/plus/1",
                "Grêmio": "https://www.transfermarkt.com/gremio-porto-alegre/kader/verein/210/saison_id/2019/plus/1",
                "Palmeiras": "https://www.transfermarkt.com/se-palmeiras-sao-paulo/kader/verein/1023/saison_id/2019/plus/1",
                "Santos": "https://www.transfermarkt.com/fc-santos/kader/verein/221/saison_id/2019/plus/1",
                "Athletico-PR": "https://www.transfermarkt.com/club-athletico-paranaense/kader/verein/679/saison_id/2019/plus/1",
                "Ceará": "https://www.transfermarkt.com/ceara-sporting-club/kader/verein/2029/saison_id/2019/plus/1",
                "Bahia": "https://www.transfermarkt.com/esporte-clube-bahia/kader/verein/10010/saison_id/2019/plus/1",
                "Bragantino": "https://www.transfermarkt.com/red-bull-bragantino/kader/verein/8793/saison_id/2019/plus/1",
                "Fortaleza": "https://www.transfermarkt.com/fortaleza-esporte-clube/kader/verein/10870/saison_id/2019/plus/1",
                "Sport": "https://www.transfermarkt.com/sport-club-do-recife/kader/verein/8718/saison_id/2019/plus/1",
                "Vasco da Gama": "https://www.transfermarkt.com/vasco-da-gama-rio-de-janeiro/kader/verein/978/saison_id/2019/plus/1",
                "Goiás": "https://www.transfermarkt.com/goias-ec/kader/verein/3197/saison_id/2019/plus/1",
                "Corinthians": "https://www.transfermarkt.com/corinthians-sao-paulo/kader/verein/199/saison_id/2019/plus/1",
                "Atlético-GO": "https://www.transfermarkt.com/atletico-clube-goianiense/kader/verein/15172/saison_id/2019/plus/1",
                "Coritiba": "https://www.transfermarkt.com/coritiba-fc/kader/verein/776/saison_id/2019/plus/1",
                "Botafogo": "https://www.transfermarkt.com/botafogo-rio-de-janeiro/kader/verein/537/saison_id/2019/plus/1"
            }
        }
        
        # Temporadas Legacy (2020-2024) e 2025 separada
        self.temporadas_legacy = ["2024", "2023", "2022", "2021", "2020"]
        self.temporada_2025 = ["2025"]
    
    def get_scraper_for_season(self, season):
        """Retorna o scraper apropriado para a temporada"""
        if season == "2025":
            return TransfermarktScraper2025()
        else:
            return TransfermarktScraperLegacy()
    
    def detect_layout_type(self, season):
        """Detecta o tipo de layout baseado na temporada"""
        if season == "2025":
            return "Layout 2025 (com contrato)"
        else:
            return "Layout Legacy (sem contrato)"
    
    def validate_and_clean_data(self, season_data, layout_type):
        """Valida e limpa dados antes do salvamento - COLUNAS PADRONIZADAS"""
        cleaned_data = []
        
        for player in season_data:
            try:
                # Validações básicas
                if not player.get('nome') or len(player['nome']) < 2:
                    continue
                
                if not player.get('numero_camisa') or not str(player['numero_camisa']).isdigit():
                    continue
                
                # Limpar e padronizar campos - ESTRUTURA UNIFICADA
                cleaned_player = {}
                
                # Campos obrigatórios
                cleaned_player['numero_camisa'] = str(player.get('numero_camisa', ''))
                cleaned_player['nome'] = str(player.get('nome', '')).strip()
                cleaned_player['clube'] = str(player.get('clube', '')).strip()
                cleaned_player['temporada'] = str(player.get('temporada', '')).strip()
                cleaned_player['layout_type'] = "2025"  # TODOS COMO 2025
                cleaned_player['data_coleta'] = str(player.get('data_coleta', ''))
                
                # Campos opcionais padronizados
                cleaned_player['posicao'] = str(player.get('posicao', '')).strip() or ""
                cleaned_player['data_nascimento'] = str(player.get('data_nascimento', '')).strip() or ""
                cleaned_player['nacionalidade'] = str(player.get('nacionalidade', '')).strip() or ""  # NOVO
                cleaned_player['clube_atual'] = str(player.get('clube_atual', '')).strip() or ""  # NOVO
                cleaned_player['altura'] = str(player.get('altura', '')).strip() or ""
                cleaned_player['pe_preferido'] = str(player.get('pe_preferido', '')).strip() or ""
                cleaned_player['data_entrada'] = str(player.get('data_entrada', '')).strip() or ""
                cleaned_player['clube_origem'] = str(player.get('clube_origem', '')).strip() or ""
                cleaned_player['contrato_ate'] = str(player.get('contrato_ate', '')).strip() or ""  # PADRONIZADO
                cleaned_player['link_perfil'] = str(player.get('link_perfil', '')).strip() or ""
                
                # Idade com validação
                idade = player.get('idade')
                if idade and isinstance(idade, (int, float)) and 15 <= idade <= 45:
                    cleaned_player['idade'] = int(idade)
                else:
                    cleaned_player['idade'] = None
                
                # Valor de mercado
                valor_texto = str(player.get('valor_mercado_texto', '')).strip()
                valor_numerico = player.get('valor_mercado_numerico', 0)
                
                if valor_texto and valor_texto not in ['', 'N/A', '-']:
                    cleaned_player['valor_mercado_texto'] = valor_texto
                else:
                    cleaned_player['valor_mercado_texto'] = ""
                
                if isinstance(valor_numerico, (int, float)) and valor_numerico >= 0:
                    cleaned_player['valor_mercado_numerico'] = int(valor_numerico)
                else:
                    cleaned_player['valor_mercado_numerico'] = 0
                
                cleaned_data.append(cleaned_player)
                
            except Exception as e:
                print(f"   ⚠️ Erro ao limpar dados do jogador: {e}")
                continue
        
        print(f"   🔧 Dados limpos: {len(cleaned_data)}/{len(season_data)} jogadores válidos")
        return cleaned_data
    
    def salvar_dados_por_temporada(self, season_data, season):
        """Salvamento seguro com estrutura unificada"""
        if not season_data:
            print(f"❌ Nenhum dado para salvar da temporada {season}")
            return None
        
        try:
            print(f"\n💾 SALVAMENTO AUTOMÁTICO - Temporada {season}...")
            layout_type = "2025"  # TODOS COMO 2025
            layout_desc = f"Layout Unificado 2025 (Temporada {season})"
            print(f"   🔧 Layout usado: {layout_desc}")
            
            # Validação e limpeza dos dados
            cleaned_data = self.validate_and_clean_data(season_data, layout_type)
            
            if not cleaned_data:
                print(f"❌ Nenhum dado válido após limpeza para temporada {season}")
                return None
            
            df = pd.DataFrame(cleaned_data)
            
            # ESTRUTURA DE COLUNAS UNIFICADA
            column_order = [
                'numero_camisa', 'nome', 'posicao', 'data_nascimento', 'idade', 
                'nacionalidade', 'clube_atual', 'altura', 'pe_preferido', 
                'data_entrada', 'clube_origem', 'contrato_ate', 'valor_mercado_texto', 
                'valor_mercado_numerico', 'clube', 'temporada', 'layout_type',
                'link_perfil', 'data_coleta'
            ]
            
            # Garantir que todas as colunas existem
            for col in column_order:
                if col not in df.columns:
                    df[col] = ""
            
            df = df[column_order]
            
            # Tratamento de dados
            string_columns = [col for col in column_order if col not in ['idade', 'valor_mercado_numerico']]
            
            for col in string_columns:
                df[col] = df[col].fillna('').astype(str)
                df[col] = df[col].replace(['None', 'nan', 'NaN'], '')
            
            # Tratar coluna idade
            df['idade'] = df['idade'].fillna('')
            df.loc[df['idade'] == '', 'idade'] = None
            
            # Tratar valor numérico
            df['valor_mercado_numerico'] = pd.to_numeric(df['valor_mercado_numerico'], errors='coerce').fillna(0).astype(int)
            
            # Ordenar dados
            df = df.sort_values(['clube', 'valor_mercado_numerico'], ascending=[True, False])
            
            # Criar diretório se não existir
            if not os.path.exists(self.default_save_path):
                os.makedirs(self.default_save_path)
                print(f"📁 Diretório criado: {self.default_save_path}")
            
            # Nome único do arquivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            filename = f"transfermarkt_brasileirao_{season}_unified_2025_{timestamp}.xlsx"
            full_path = os.path.join(self.default_save_path, filename)
            
            # SALVAMENTO SEGURO COM MÚLTIPLAS ABAS
            with pd.ExcelWriter(full_path, engine='openpyxl') as writer:
                # 1. Aba principal da temporada
                df.to_excel(writer, sheet_name=f'Temporada_{season}', index=False)
                print(f"   ✅ Aba principal criada: Temporada_{season}")
                
                # 2. Abas por time
                teams_count = 0
                for team in df['clube'].unique():
                    team_df = df[df['clube'] == team]
                    sheet_name = team[:31] if len(team) > 31 else team
                    sheet_name = re.sub(r'[^\w\s-]', '', sheet_name)
                    team_df.to_excel(writer, sheet_name=sheet_name, index=False)
                    teams_count += 1
                
                print(f"   ✅ {teams_count} abas de times criadas")
                
                # 3. Aba de estatísticas
                try:
                    total_jogadores = len(df)
                    total_times = df['clube'].nunique()
                    
                    # Nacionalidades mais comuns
                    nacionalidades_count = df[df['nacionalidade'] != '']['nacionalidade'].value_counts().head(10)
                    
                    # Clubes atuais mais comuns (para legacy)
                    clubes_atuais_count = df[df['clube_atual'] != '']['clube_atual'].value_counts().head(10)
                    
                    # Valor total e médio
                    valores_validos = df[df['valor_mercado_numerico'] > 0]['valor_mercado_numerico']
                    valor_total = valores_validos.sum() if len(valores_validos) > 0 else 0
                    valor_medio = valores_validos.mean() if len(valores_validos) > 0 else 0
                    
                    # Idade média
                    idades_validas = df[df['idade'].notna() & (df['idade'] > 0)]['idade']
                    idade_media = idades_validas.mean() if len(idades_validas) > 0 else 0
                    
                    stats_data = {
                        'Métrica': [
                            'Total de Jogadores',
                            'Total de Times',
                            'Jogadores com Nacionalidade',
                            'Jogadores com Clube Atual',
                            'Jogadores com Contrato',
                            'Jogadores com Valor Definido',
                            'Jogadores com Idade Definida',
                            'Valor Total do Elenco (€)',
                            'Valor Médio por Jogador (€)',
                            'Idade Média',
                            'Layout da Tabela',
                            'Nacionalidade Mais Comum',
                            'Clube Atual Mais Comum'
                        ],
                        'Valor': [
                            total_jogadores,
                            total_times,
                            len(df[df['nacionalidade'] != '']),
                            len(df[df['clube_atual'] != '']),
                            len(df[df['contrato_ate'] != '']),
                            len(valores_validos),
                            len(idades_validas),
                            f"{valor_total:,.0f}",
                            f"{valor_medio:,.0f}",
                            f"{idade_media:.1f} anos" if idade_media > 0 else "N/A",
                            "Estrutura Unificada 2025",
                            nacionalidades_count.index[0] if len(nacionalidades_count) > 0 else "N/A",
                            clubes_atuais_count.index[0] if len(clubes_atuais_count) > 0 else "N/A"
                        ]
                    }
                    
                    stats_df = pd.DataFrame(stats_data)
                    stats_df.to_excel(writer, sheet_name='Estatisticas', index=False)
                    print(f"   ✅ Aba de estatísticas criada")
                    
                except Exception as e:
                    print(f"   ⚠️ Erro ao criar estatísticas: {e}")
            
            # Verificar se arquivo foi salvo com sucesso
            if os.path.exists(full_path):
                file_size = os.path.getsize(full_path) / 1024  # KB
                print(f"\n🎉 SALVAMENTO CONCLUÍDO!")
                print(f"✅ Arquivo: {filename}")
                print(f"📊 {len(df)} jogadores, {df['clube'].nunique()} times")
                print(f"🔧 Estrutura: UNIFICADA (todas as colunas padronizadas)")
                print(f"📁 Local: {full_path}")
                print(f"💾 Tamanho: {file_size:.1f} KB")
                print(f"🔒 DADOS SEGUROS - Temporada {season}")
                
                return full_path
            else:
                print(f"❌ Erro: Arquivo não foi criado")
                return None
            
        except Exception as e:
            print(f"❌ ERRO CRÍTICO ao salvar temporada {season}: {e}")
            return None
    
    def mostrar_menu_principal(self):
        """Exibe menu principal com opções de scraping"""
        print("\n⚽ TRANSFERMARKT BRASILEIRÃO SCRAPER - ESTRUTURA UNIFICADA")
        print("=" * 80)
        print("🔧 NOVIDADES DA ATUALIZAÇÃO:")
        print("   ✅ Ambas tabelas (Legacy e 2025) têm as MESMAS COLUNAS")
        print("   ✅ Campo 'nacionalidade' adicionado em ambas")
        print("   ✅ Campo 'clube_atual' padronizado")
        print("   ✅ Campo 'layout_type' = '2025' para todos")
        print("   ✅ Problema idade/data_nascimento CORRIGIDO")
        print("\n📊 OPÇÕES DISPONÍVEIS:")
        print("1. 🎯 Scraping 2025 (Layout 2025 - 20 times)")
        print("2. 🎯 Scraping por temporada individual (2020-2024)")
        print("3. 🚀 Scraping TODAS as temporadas Legacy (2020-2024)")
        print("4. 📂 Verificar arquivos existentes")
        print("0. ❌ Sair")
        print("=" * 80)
    
    def mostrar_menu_temporadas_legacy(self):
        """Exibe menu de temporadas legacy"""
        print("\n📅 TEMPORADAS LEGACY DISPONÍVEIS (2020-2024):")
        print("=" * 60)
        
        for i, season in enumerate(self.temporadas_legacy, 1):
            times_count = len(self.times_por_temporada[season])
            print(f"{i:>2}. {season} ({times_count} times) - Estrutura Unificada")
        
        print("=" * 60)
    
    def scrape_temporada_2025(self):
        """Scraping específico para 2025"""
        print(f"\n🚀 INICIANDO SCRAPING 2025")
        print(f"🔧 Scraper: TransfermarktScraper2025")
        print(f"📊 Layout: Estrutura Unificada 2025")
        print(f"🏆 Times: 20 times do Brasileirão 2025")
        print("=" * 60)
        
        season = "2025"
        teams = self.times_por_temporada[season]
        
        scraper = self.get_scraper_for_season(season)
        scraper.setup_driver()
        
        season_players_data = []
        teams_processed = 0
        
        try:
            for team_name, team_url in teams.items():
                try:
                    print(f"\n[{teams_processed + 1}/20] Processando {team_name}...")
                    
                    team_data = scraper.scrape_team_players(team_name, team_url, season)
                    
                    if team_data:
                        season_players_data.extend(team_data)
                        teams_processed += 1
                        print(f"✅ {team_name} concluído - {len(team_data)} jogadores")
                    else:
                        print(f"❌ Falha ao coletar dados de {team_name}")
                    
                    time.sleep(3)
                    
                except Exception as e:
                    print(f"❌ Erro ao processar {team_name}: {e}")
                    continue
        
        finally:
            if scraper.driver:
                scraper.driver.quit()
                print(f"🔒 Driver fechado")
        
        # Salvamento automático
        print(f"\n💾 SALVAMENTO AUTOMÁTICO - 2025")
        excel_file = self.salvar_dados_por_temporada(season_players_data, season)
        
        print(f"\n📊 RESUMO 2025:")
        print(f"   ✅ Times processados: {teams_processed}/20")
        print(f"   👥 Jogadores coletados: {len(season_players_data)}")
        print(f"   💾 Arquivo salvo: {'✅ PROTEGIDO' if excel_file else '❌ FALHOU'}")
        
        return excel_file
    
    def scrape_temporada_individual(self, season):
        """Scraping de uma temporada específica (2020-2024)"""
        print(f"\n🚀 INICIANDO SCRAPING {season}")
        print(f"🔧 Scraper: TransfermarktScraperLegacy")
        print(f"📊 Layout: Estrutura Unificada 2025")
        
        teams = self.times_por_temporada[season]
        times_count = len(teams)
        print(f"🏆 Times: {times_count} times do Brasileirão {season}")
        print("=" * 60)
        
        scraper = self.get_scraper_for_season(season)
        scraper.setup_driver()
        
        season_players_data = []
        teams_processed = 0
        
        try:
            for team_name, team_url in teams.items():
                try:
                    print(f"\n[{teams_processed + 1}/{times_count}] Processando {team_name}...")
                    
                    team_data = scraper.scrape_team_players(team_name, team_url, season)
                    
                    if team_data:
                        season_players_data.extend(team_data)
                        teams_processed += 1
                        print(f"✅ {team_name} concluído - {len(team_data)} jogadores")
                    else:
                        print(f"❌ Falha ao coletar dados de {team_name}")
                    
                    time.sleep(3)
                    
                except Exception as e:
                    print(f"❌ Erro ao processar {team_name}: {e}")
                    continue
        
        finally:
            if scraper.driver:
                scraper.driver.quit()
                print(f"🔒 Driver fechado")
        
        # Salvamento automático
        print(f"\n💾 SALVAMENTO AUTOMÁTICO - {season}")
        excel_file = self.salvar_dados_por_temporada(season_players_data, season)
        
        print(f"\n📊 RESUMO {season}:")
        print(f"   ✅ Times processados: {teams_processed}/{times_count}")
        print(f"   👥 Jogadores coletados: {len(season_players_data)}")
        print(f"   💾 Arquivo salvo: {'✅ PROTEGIDO' if excel_file else '❌ FALHOU'}")
        
        return excel_file
    
    def scrape_todas_temporadas_legacy(self):
        """Scraping de todas as temporadas legacy (2020-2024)"""
        print(f"\n🚀 INICIANDO SCRAPING COMPLETO LEGACY (2020-2024)")
        print(f"🔧 Scraper: TransfermarktScraperLegacy")
        print(f"📊 Layout: Estrutura Unificada 2025")
        print(f"📅 Temporadas: {', '.join(self.temporadas_legacy)}")
        print(f"🏆 Total estimado: ~100 times")
        print(f"⏱️ Tempo estimado: 2-4 horas")
        print("=" * 80)
        
        confirmar = input("\nDeseja continuar com TODAS as temporadas legacy? (s/n): ").strip().lower()
        if confirmar != 's':
            print("❌ Scraping cancelado pelo usuário.")
            return
        
        all_files = []
        
        for season_idx, season in enumerate(self.temporadas_legacy):
            print(f"\n{'='*60}")
            print(f"📅 TEMPORADA {season} ({season_idx + 1}/{len(self.temporadas_legacy)})")
            print(f"{'='*60}")
            
            excel_file = self.scrape_temporada_individual(season)
            
            if excel_file:
                all_files.append({
                    'season': season,
                    'file': excel_file,
                    'success': True
                })
            else:
                all_files.append({
                    'season': season,
                    'file': None,
                    'success': False
                })
            
            # Pausa entre temporadas
            if season_idx < len(self.temporadas_legacy) - 1:
                print(f"\n⏱️ Pausa de 10 segundos antes da próxima temporada...")
                time.sleep(10)
        
        # Relatório final
        successful_files = [f for f in all_files if f['success']]
        
        print(f"\n🎉 SCRAPING LEGACY FINALIZADO!")
        print(f"✅ {len(successful_files)}/{len(all_files)} temporadas coletadas")
        print(f"🔧 Estrutura: UNIFICADA (todas as colunas padronizadas)")
        print(f"📁 Todos os arquivos em: {self.default_save_path}")
        
        if successful_files:
            print(f"\n📂 ARQUIVOS CRIADOS:")
            for file_info in successful_files:
                filename = os.path.basename(file_info['file'])
                print(f"   ✅ {file_info['season']}: {filename}")
        
        failed_files = [f for f in all_files if not f['success']]
        if failed_files:
            print(f"\n⚠️ TEMPORADAS COM FALHA:")
            for file_info in failed_files:
                print(f"   ❌ {file_info['season']}")
    
    def verificar_arquivos_existentes(self):
        """Verifica quais temporadas já foram coletadas"""
        if not os.path.exists(self.default_save_path):
            print(f"\n📂 Diretório não existe: {self.default_save_path}")
            return
        
        arquivos_existentes = []
        for arquivo in os.listdir(self.default_save_path):
            if arquivo.startswith('transfermarkt_brasileirao_') and arquivo.endswith('.xlsx'):
                try:
                    parts = arquivo.split('_')
                    if len(parts) >= 4:
                        temporada = parts[2]
                        layout_type = parts[3] if 'unified' not in parts[3] else 'unified'
                        arquivos_existentes.append({
                            'temporada': temporada,
                            'layout_type': layout_type,
                            'arquivo': arquivo
                        })
                except:
                    continue
        
        if arquivos_existentes:
            print(f"\n📂 ARQUIVOS JÁ COLETADOS ({len(arquivos_existentes)}):")
            print("=" * 80)
            
            # Agrupar por layout
            legacy_files = [f for f in arquivos_existentes if f['layout_type'] == 'legacy']
            files_2025 = [f for f in arquivos_existentes if f['layout_type'] == '2025']
            unified_files = [f for f in arquivos_existentes if f['layout_type'] == 'unified']
            
            if unified_files:
                print("\n🔧 ESTRUTURA UNIFICADA:")
                for arquivo in unified_files:
                    print(f"   ✅ {arquivo['temporada']}: {arquivo['arquivo']}")
            
            if files_2025:
                print("\n🔧 LAYOUT 2025 (ANTIGO):")
                for arquivo in files_2025:
                    print(f"   📅 {arquivo['temporada']}: {arquivo['arquivo']}")
            
            if legacy_files:
                print("\n🔧 LAYOUT LEGACY (ANTIGO):")
                for arquivo in legacy_files:
                    print(f"   📅 {arquivo['temporada']}: {arquivo['arquivo']}")
            
            print("=" * 80)
        else:
            print(f"\n📂 Nenhum arquivo anterior encontrado em: {self.default_save_path}")
    
    def executar(self):
        """Método principal com menu interativo"""
        try:
            while True:
                self.mostrar_menu_principal()
                
                escolha = input("\n🔢 Digite sua opção: ").strip()
                
                if escolha == "0":
                    print("👋 Encerrando programa. Até logo!")
                    break
                
                elif escolha == "1":
                    # Scraping 2025
                    self.scrape_temporada_2025()
                    input("\n⏸️ Pressione Enter para continuar...")
                
                elif escolha == "2":
                    # Scraping temporada individual
                    while True:
                        self.mostrar_menu_temporadas_legacy()
                        
                        escolha_temp = input("\n🔢 Digite o número da temporada (0 para voltar): ").strip()
                        
                        if escolha_temp == "0":
                            break
                        
                        try:
                            escolha_num = int(escolha_temp)
                            if 1 <= escolha_num <= len(self.temporadas_legacy):
                                season = self.temporadas_legacy[escolha_num - 1]
                                self.scrape_temporada_individual(season)
                                input("\n⏸️ Pressione Enter para continuar...")
                                break
                            else:
                                print("❌ Opção inválida!")
                        except ValueError:
                            print("❌ Digite um número válido!")
                
                elif escolha == "3":
                    # Scraping todas as temporadas legacy
                    self.scrape_todas_temporadas_legacy()
                    input("\n⏸️ Pressione Enter para continuar...")
                
                elif escolha == "4":
                    # Verificar arquivos existentes
                    self.verificar_arquivos_existentes()
                    input("\n⏸️ Pressione Enter para continuar...")
                
                else:
                    print("❌ Opção inválida! Tente novamente.")
                    
        except KeyboardInterrupt:
            print("\n\n⏹️ PROGRAMA INTERROMPIDO PELO USUÁRIO")
            print(f"🔒 DADOS JÁ PROCESSADOS ESTÃO SEGUROS!")
            print(f"📁 Verificar arquivos em: {self.default_save_path}")
        except Exception as e:
            print(f"\n❌ Erro na execução: {e}")
            print(f"🔒 DADOS PROCESSADOS ESTÃO SEGUROS!")
            print(f"📁 Verificar arquivos salvos em: {self.default_save_path}")

def main():
    """Função principal"""
    print("🚀 TRANSFERMARKT BRASILEIRÃO SCRAPER - ESTRUTURA UNIFICADA")
    print("🔧 PRINCIPAIS MELHORIAS:")
    print("   ✅ Ambas tabelas (Legacy e 2025) com MESMAS COLUNAS")
    print("   ✅ Campo 'nacionalidade' extraído automaticamente")
    print("   ✅ Campo 'clube_atual' padronizado (sem datas)")
    print("   ✅ Campo 'layout_type' = '2025' para todos")
    print("   ✅ Problema idade/data_nascimento CORRIGIDO")
    print("   ✅ Estrutura de dados 100% compatível")
    print("=" * 80)
    
    scraper = TransfermarktJogadores()
    scraper.executar()

if __name__ == "__main__":
    main()