---
title: "Сравнение ethers.js, viem, wagmi"
date: 2026-07-09
tags: [web3, инструменты, ethers, viem, wagmi, сравнение]
category: analysis
---

# Сравнение ethers.js, viem, wagmi

Три основных инструмента для фронтенда, чтобы общаться с блокчейном. Какой и когда использовать?

## ethers.js v6

**Что это:** низкоуровневая библиотека для взаимодействия с Ethereum. Прямой аналог web3.js, но современнее и легче.

**Что умеет:**
- Подключаться к нодам через JSON-RPC
- Читать данные из контрактов (`contract.balanceOf()`)
- Отправлять транзакции (`contract.transfer()`)
- Слушать события (`contract.on("Transfer", ...)`)
- Работать с кошельками, подписывать сообщения

**Плюсы:**
- Зрелая, самая популярная библиотека
- Огромное количество примеров и туториалов
- Полный контроль над всем

**Минусы:**
- Тяжёлая (~500 KB бандл)
- Не tree-shakeable
- API местами неинтуитивно (особенно BigNumber в v5, в v6 улучшили)

**Когда использовать:** если нужен полный контроль и не пугает большой бандл.

---

## viem

**Что это:** современная альтернатива ethers.js от создателей wagmi.

**Что умеет:** то же самое, что ethers.js, но:

**Плюсы:**
- Лёгкая (~50 KB, tree-shakeable)
- TypeScript-first (типы из коробки, без доп. пакетов)
- Современное API: compose-able, предсказуемое
- Быстрее развивается

**Минусы:**
- Меньше туториалов и примеров (но быстро догоняет)
- API отличается от ethers.js — нужно переучиваться

**Когда использовать:** новые проекты 2024+. Рекомендуемый выбор.

---

## wagmi

**Что это:** React-хуки поверх viem (работает с viem v2, раньше работала с ethers.js).

**Что умеет:**
- `useAccount()` — подключён ли кошелёк, какой адрес
- `useConnect()` — диалог «подключить MetaMask»
- `useReadContract()` — прочитать данные из контракта
- `useWriteContract()` — отправить транзакцию
- `useWaitForTransactionReceipt()` — ждать подтверждения
- `useWatchContractEvent()` — слушать события

**Плюсы:**
- Декларативный React-подход — меньше бойлерплейта
- Автоматический refetch при смене аккаунта/сети
- Кэширование, инвалидация запросов
- Интеграция с RainbowKit (UI для connect wallet)

**Минусы:**
- Абстракция — сложнее понять, что под капотом
- Зависимость от React

**Когда использовать:** всегда, если пишем на React. wagmi + viem = золотой стандарт 2024+.

---

## Как они соотносятся

```
Уровень абстракции:
  wagmi        ← React-хуки (самый высокий уровень)
    ↓
  viem         ← низкоуровневые вызовы (легковесный)
    ↓
  ethers.js    ← низкоуровневые вызовы (тяжёлый)

Иерархия:
  wagmi использует viem
  viem — самостоятельная библиотека
  ethers.js — самостоятельная библиотека
```

---

## Рекомендация для пет-проекта

```
React + TypeScript
    + wagmi        (хуки: connect, read, write)
    + viem         (идет внутри wagmi, редко напрямую)
    + RainbowKit   (UI для кнопки "Connect Wallet")
```

**Не рекомендую** ethers.js для новых проектов — viem легче, быстрее, и wagmi перешёл на viem.

## Минимальный пример (wagmi + viem)

```tsx
import { useAccount, useReadContract, useWriteContract } from 'wagmi';

function TokenBalance() {
  const { address } = useAccount();

  const { data: balance } = useReadContract({
    address: '0x...', // адрес токена
    abi: erc20Abi,
    functionName: 'balanceOf',
    args: [address],
  });

> **Как читать `useReadContract({ address: '0x...', abi: erc20Abi, functionName: 'balanceOf', args: [address] })`:** «React-хуком прочитай баланс ERC-20 токена: вызови view-функцию `balanceOf` у контракта по адресу, с типовым ABI стандартного токена, передав адрес пользователя». Мнемоника: адрес + ABI + функция + аргументы = один декларативный запрос, без бойлерплейта.

  const { writeContract } = useWriteContract();

  return (
    <div>
      <p>Баланс: {balance?.toString()}</p>
      <button onClick={() => writeContract({
        address: '0x...',
        abi: erc20Abi,
        functionName: 'transfer',
        args: ['0xRecipient...', 100n],
      })}>
        Отправить 100 токенов
      </button>
    </div>
  );
}
```

> **Как читать `writeContract({ address: '0x...', abi: erc20Abi, functionName: 'transfer', args: ['0xRecipient...', 100n] })`:** «пошли транзакцию перевода токенов на смарт-контракт: вызови `transfer`, передав адрес получателя и количество в минимальных единицах (BigInt с суффиксом `n`)». Мнемоника: `writeContract` = мутация блокчейна; жди подпись в кошельке, потом отслеживай через хеш.
