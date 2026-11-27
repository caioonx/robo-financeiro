-- ==========================================
-- ROBO FINANCEIRO
-- Base de dados demonstrativa
-- Dados exclusivamente ficticios
-- ==========================================

-- Banco separado para proteger os dados reais
USE empresa_automacao_demo;

START TRANSACTION;

-- ==========================================
-- CLIENTES FICTICIOS
-- ==========================================

INSERT INTO clientes
(nome, cpf_cnpj, email, cidade)
VALUES
('Cliente Demo 01', 'DEMO-001',
 'cliente1@example.com', 'Goiania'),

('Cliente Demo 02', 'DEMO-002',
 'cliente2@example.com', 'Brasilia'),

('Cliente Demo 03', 'DEMO-003',
 'cliente3@example.com', 'Sao Paulo'),

('Cliente Demo 04', 'DEMO-004',
 'cliente4@example.com', 'Curitiba'),

('Cliente Demo 05', 'DEMO-005',
 'cliente5@example.com', 'Belo Horizonte');

-- ==========================================
-- FORNECEDORES FICTICIOS
-- ==========================================

INSERT INTO fornecedores
(razao_social, cnpj, email, categoria, cidade)
VALUES
('Demo Tecnologia', 'DEMO-F001',
 'tecnologia@example.com', 'Tecnologia', 'Sao Paulo'),

('Demo Energia', 'DEMO-F002',
 'energia@example.com', 'Energia', 'Goiania'),

('Demo Telecom', 'DEMO-F003',
 'telecom@example.com', 'Telecomunicacoes', 'Brasilia'),

('Demo Imoveis', 'DEMO-F004',
 'imoveis@example.com', 'Locacao', 'Goiania'),

('Demo Suprimentos', 'DEMO-F005',
 'suprimentos@example.com', 'Material de escritorio', 'Goiania'),

('Demo Consultoria', 'DEMO-F006',
 'consultoria@example.com', 'Consultoria', 'Sao Paulo'),

('Demo Logistica', 'DEMO-F007',
 'logistica@example.com', 'Transporte', 'Curitiba'),

('Demo Software', 'DEMO-F008',
 'software@example.com', 'Software', 'Brasilia');

-- ==========================================
-- IDENTIFICACAO DOS FORNECEDORES
-- ==========================================

SET @f1 = (SELECT id_fornecedor FROM fornecedores
WHERE cnpj = 'DEMO-F001');

SET @f2 = (SELECT id_fornecedor FROM fornecedores
WHERE cnpj = 'DEMO-F002');

SET @f3 = (SELECT id_fornecedor FROM fornecedores
WHERE cnpj = 'DEMO-F003');

SET @f4 = (SELECT id_fornecedor FROM fornecedores
WHERE cnpj = 'DEMO-F004');

SET @f5 = (SELECT id_fornecedor FROM fornecedores
WHERE cnpj = 'DEMO-F005');

SET @f6 = (SELECT id_fornecedor FROM fornecedores
WHERE cnpj = 'DEMO-F006');

SET @f7 = (SELECT id_fornecedor FROM fornecedores
WHERE cnpj = 'DEMO-F007');

SET @f8 = (SELECT id_fornecedor FROM fornecedores
WHERE cnpj = 'DEMO-F008');

-- ==========================================
-- CONTAS VENCIDAS
-- ==========================================

INSERT INTO contas_pagar
(id_fornecedor, descricao, valor,
 vencimento, data_pagamento, status)
VALUES
(@f1, 'Manutencao de equipamentos', 4500.00,
 CURDATE() - INTERVAL 15 DAY, NULL, 'VENCIDO'),

(@f2, 'Energia eletrica', 1800.00,
 CURDATE() - INTERVAL 8 DAY, NULL, 'VENCIDO'),

(@f3, 'Internet empresarial', 700.00,
 CURDATE() - INTERVAL 5 DAY, NULL, 'VENCIDO'),

(@f6, 'Consultoria administrativa', 5000.00,
 CURDATE() - INTERVAL 20 DAY, NULL, 'VENCIDO');

-- ==========================================
-- CONTAS PENDENTES
-- ==========================================

INSERT INTO contas_pagar
(id_fornecedor, descricao, valor,
 vencimento, data_pagamento, status)
VALUES
(@f4, 'Aluguel comercial', 6500.00,
 CURDATE() + INTERVAL 10 DAY, NULL, 'PENDENTE'),

(@f8, 'Licencas de software', 3200.00,
 CURDATE() + INTERVAL 15 DAY, NULL, 'PENDENTE'),

(@f5, 'Material de escritorio', 1200.00,
 CURDATE() + INTERVAL 7 DAY, NULL, 'PENDENTE'),

(@f7, 'Servicos de transporte', 2800.00,
 CURDATE() + INTERVAL 12 DAY, NULL, 'PENDENTE'),

(@f1, 'Equipamentos de informatica', 5800.00,
 CURDATE() + INTERVAL 25 DAY, NULL, 'PENDENTE');

-- ==========================================
-- CONTAS PAGAS
-- ==========================================

INSERT INTO contas_pagar
(id_fornecedor, descricao, valor,
 vencimento, data_pagamento, status)
VALUES
(@f4, 'Aluguel do mes anterior', 6500.00,
 CURDATE() - INTERVAL 30 DAY,
 CURDATE() - INTERVAL 31 DAY, 'PAGO'),

(@f2, 'Energia do mes anterior', 1700.00,
 CURDATE() - INTERVAL 25 DAY,
 CURDATE() - INTERVAL 26 DAY, 'PAGO'),

(@f3, 'Telefonia empresarial', 600.00,
 CURDATE() - INTERVAL 12 DAY,
 CURDATE() - INTERVAL 13 DAY, 'PAGO'),

(@f5, 'Compra de suprimentos', 900.00,
 CURDATE() - INTERVAL 10 DAY,
 CURDATE() - INTERVAL 11 DAY, 'PAGO'),

(@f8, 'Assinatura de sistemas', 2300.00,
 CURDATE() - INTERVAL 18 DAY,
 CURDATE() - INTERVAL 19 DAY, 'PAGO'),

(@f7, 'Fretes e entregas', 4000.00,
 CURDATE() - INTERVAL 6 DAY,
 CURDATE() - INTERVAL 7 DAY, 'PAGO');

COMMIT;

-- ==========================================
-- FIM DOS DADOS DEMONSTRATIVOS
-- ==========================================