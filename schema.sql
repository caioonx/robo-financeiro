-- ==========================================
-- ROBO FINANCEIRO
-- Estrutura do banco de dados
-- MySQL 8.0+
-- ==========================================

CREATE DATABASE IF NOT EXISTS empresa_automacao_demo
CHARACTER SET utf8mb4
COLLATE utf8mb4_0900_ai_ci;

USE empresa_automacao_demo;

-- ==========================================
-- TABELA DE CLIENTES
-- ==========================================

CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INT NOT NULL AUTO_INCREMENT,
    nome VARCHAR(150) NOT NULL,
    cpf_cnpj VARCHAR(18) NOT NULL,
    email VARCHAR(150) DEFAULT NULL,
    telefone VARCHAR(20) DEFAULT NULL,
    cidade VARCHAR(100) DEFAULT NULL,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('ATIVO', 'INATIVO') DEFAULT 'ATIVO',

    PRIMARY KEY (id_cliente),
    UNIQUE KEY (cpf_cnpj)
) ENGINE=InnoDB;

-- ==========================================
-- TABELA DE FORNECEDORES
-- ==========================================

CREATE TABLE IF NOT EXISTS fornecedores (
    id_fornecedor INT NOT NULL AUTO_INCREMENT,
    razao_social VARCHAR(150) NOT NULL,
    cnpj VARCHAR(18) NOT NULL,
    email VARCHAR(150) DEFAULT NULL,
    telefone VARCHAR(20) DEFAULT NULL,
    categoria VARCHAR(100) DEFAULT NULL,
    cidade VARCHAR(100) DEFAULT NULL,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('ATIVO', 'INATIVO') DEFAULT 'ATIVO',

    PRIMARY KEY (id_fornecedor),
    UNIQUE KEY (cnpj)
) ENGINE=InnoDB;

-- ==========================================
-- TABELA DE CONTAS A PAGAR
-- ==========================================

CREATE TABLE IF NOT EXISTS contas_pagar (
    id_conta INT NOT NULL AUTO_INCREMENT,
    id_fornecedor INT NOT NULL,
    descricao VARCHAR(200) NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    vencimento DATE NOT NULL,
    data_pagamento DATE DEFAULT NULL,
    status ENUM(
        'PENDENTE',
        'PAGO',
        'VENCIDO'
    ) NOT NULL DEFAULT 'PENDENTE',

    PRIMARY KEY (id_conta),

    KEY id_fornecedor (id_fornecedor),

    CONSTRAINT contas_pagar_ibfk_1
        FOREIGN KEY (id_fornecedor)
        REFERENCES fornecedores (id_fornecedor)

) ENGINE=InnoDB;

-- ==========================================
-- TABELA DE LOGS DA AUTOMACAO
-- ==========================================

CREATE TABLE IF NOT EXISTS logs_automacao (
    id_log INT NOT NULL AUTO_INCREMENT,
    nome_robo VARCHAR(100) NOT NULL,
    data_execucao DATETIME DEFAULT CURRENT_TIMESTAMP,
    registros_atualizados INT NOT NULL,
    mensagem VARCHAR(255) DEFAULT NULL,

    PRIMARY KEY (id_log)
) ENGINE=InnoDB;

-- ==========================================
-- EVENTO AUTOMATICO DE CONTAS VENCIDAS
-- ==========================================

DELIMITER $$

CREATE EVENT IF NOT EXISTS robo_contas_vencidas

ON SCHEDULE EVERY 1 MINUTE

ON COMPLETION PRESERVE

DISABLE

DO
BEGIN

    DECLARE total_atualizados INT DEFAULT 0;

    UPDATE contas_pagar
    SET status = 'VENCIDO'
    WHERE vencimento < CURDATE()
      AND status = 'PENDENTE'
      AND data_pagamento IS NULL;

    SET total_atualizados = ROW_COUNT();

    IF total_atualizados > 0 THEN

        INSERT INTO logs_automacao (
            nome_robo,
            registros_atualizados,
            mensagem
        )
        VALUES (
            'robo_contas_vencidas',
            total_atualizados,
            'Rotina executada com sucesso'
        );

    END IF;

END$$

DELIMITER ;

-- ==========================================
-- FIM DA ESTRUTURA DO BANCO
-- ==========================================