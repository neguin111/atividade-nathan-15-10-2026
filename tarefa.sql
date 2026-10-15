CREATE DATABASE IF NOT EXISTS db_nh_smartbox;
USE db_nh_smartbox;

-- 1. Tabela de Utilizadores (com coluna de senha ajustada para VARCHAR(255))
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    login VARCHAR(50) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    tipo VARCHAR(20) DEFAULT "Morador"
);

-- 2. Tabela de Credenciais de Acesso
CREATE TABLE IF NOT EXISTS credenciais_acesso (
    id_credencial INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    codigo_senha VARCHAR(50) UNIQUE NOT NULL,
    descricao VARCHAR(100),
    tipo VARCHAR(30) NOT NULL,
    status VARCHAR(20) DEFAULT "Ativa",
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

-- 3. Tabela de Entregas
CREATE TABLE IF NOT EXISTS entregas (
    id_entrega INT AUTO_INCREMENT PRIMARY KEY,
    codigo_rastreio VARCHAR(50),
    remetente VARCHAR(100),
    distancia_cm FLOAT NOT NULL,
    status_encomenda VARCHAR(30) DEFAULT "Depositado"
);

-- 4. Tabela de Logs do Sistema
CREATE TABLE IF NOT EXISTS logs_sistema (
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    metodo_acesso VARCHAR(50) NOT NULL,
    credencial_usada VARCHAR(50),
    acao_executada VARCHAR(100) NOT NULL
);

-- -----------------------------------------------------
-- INSERÇÃO DE DADOS DE TESTE (Senhas com Hash válido)
-- -----------------------------------------------------

-- Limpa registos prévios para evitar erros de duplicado (opcional)
TRUNCATE TABLE credenciais_acesso;
DELETE FROM usuarios;

-- Insere utilizadores com o HASH correto da palavra-passe "123456"
INSERT INTO usuarios (id_usuario, nome, login, senha, tipo) VALUES 
(1, "Lucas Silva", "lucas.silva", "pbkdf2:sha256:260000$bv4e0G6J$156555ddf3595eb9c08a1012398da13e3bc3f1362e7428f522e8dfec30efd914", "Morador"),
(2, "Maria Oliveira", "maria.oliveira", "pbkdf2:sha256:260000$bv4e0G6J$156555ddf3595eb9c08a1012398da13e3bc3f1362e7428f522e8dfec30efd914", "Admin");

-- Insere credenciais vinculadas
INSERT INTO credenciais_acesso (id_usuario, codigo_senha, descricao, tipo, status) VALUES 
(1, "730192", "Mercado Livre", "Senha Temporaria", "Ativa"),
(2, "TAG-01", "Tag Entregador", "RFID", "Ativa");

-- Insere registos de entregas
INSERT INTO entregas (codigo_rastreio, remetente, distancia_cm, status_encomenda) VALUES 
("BR123456789", "Correios", 12.5, "Depositado");

-- Insere registos de logs
INSERT INTO logs_sistema (metodo_acesso, credencial_usada, acao_executada) VALUES 
("Senha Temporaria", "730192", "Trava liberada");