---
title: "wagmi + RainbowKit: фронтенд для dApps"
date: 2026-07-19
tags: [web3, react, wagmi, фронтенд]
category: tool
---

# wagmi + RainbowKit: фронтенд для dApps

**Современный стек для React-фронтенда web3-приложений.** wagmi даёт React-хуки для чтения и записи в блокчейн, RainbowKit — готовый UI для подключения кошелька, viem — низкоуровневый движок под капотом.

> **Актуальность:** июль 2026, wagmi v3, viem v2.x, RainbowKit v2.x. API проверен по официальной документации.

## Связь wagmi, RainbowKit и viem

```
┌──────────────────────────────────────┐
│  RainbowKit   ← Готовый UI (кнопка,  │
│                  модалки, темы)       │
├──────────────────────────────────────┤
│  wagmi        ← React-хуки           │
│  (useConnection, useReadContract...)  │
├──────────────────────────────────────┤
│  viem         ← Низкоуровневые вызовы │
│  (getBalance, sendTransaction...)     │
└──────────────────────────────────────┘
```

- **viem** — лёгкая TypeScript-библиотека для JSON-RPC запросов к Ethereum (аналог ethers.js, но современнее). Создана той же командой (wevm).
- **wagmi** — React-хуки поверх viem. Даёт `useConnection`, `useReadContract`, `useWriteContract` и ещё 60+ хуков.
- **RainbowKit** — UI-библиотека поверх wagmi. Кнопка «Connect Wallet», модалка выбора кошелька, смена сети — из коробки.

**Мнемоника:** viem — двигатель, wagmi — руль, RainbowKit — приборная панель.

---

## Уровень 1. wagmi: React-хуки

### Установка и настройка

```bash
npm install wagmi viem@2.x @tanstack/react-query
```

**config.ts** — создаём конфигурацию:

```ts
import { createConfig, http } from 'wagmi'
import { mainnet, sepolia } from 'wagmi/chains'
import { injected, walletConnect } from 'wagmi/connectors'

const projectId = 'ВАШ_WALLETCONNECT_PROJECT_ID' // бесплатно на cloud.walletconnect.com

export const config = createConfig({
  chains: [mainnet, sepolia],
  connectors: [
    injected(),                        // MetaMask и другие браузерные
    walletConnect({ projectId }),      // WalletConnect (мобильные)
  ],
  transports: {
    [mainnet.id]: http(),              // публичный RPC
    [sepolia.id]: http(),
  },
})
```

**App.tsx** — оборачиваем приложение в провайдеры:

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { WagmiProvider } from 'wagmi'
import { config } from './config'

const queryClient = new QueryClient()

function App() {
  return (
    <WagmiProvider config={config}>
      <QueryClientProvider client={queryClient}>
        {/* Ваше приложение */}
      </QueryClientProvider>
    </WagmiProvider>
  )
}
```

> **TanStack Query** обязателен в wagmi v3 — он отвечает за кэширование, дедупликацию и автоматический рефетч.

---

### useConnection — статус подключения

**На смену `useAccount` (wagmi v2) пришёл `useConnection` (wagmi v3).** Возвращает адрес, сеть, статус подключения.

```tsx
import { useConnection } from 'wagmi'

function AccountInfo() {
  const { address, chain, isConnected, status } = useConnection()

  if (status === 'connecting') return <div>Подключение...</div>
  if (!isConnected) return <div>Кошелёк не подключён</div>

> **Как читать `const { address, chain, isConnected, status } = useConnection()`:** «узнай состояние кошелька одним хуком: подключён ли, какой адрес, в какой сети, и что сейчас происходит — `'connecting'`, `'connected'` или `'disconnected'`». Мнемоника: `useConnection` = датчик кошелька: кто подключён, где находится, жив ли.

  return (
    <div>
      <p>Адрес: {address}</p>
      <p>Сеть: {chain?.name} (chainId: {chain?.id})</p>
    </div>
  )
}
```

**Ключевые поля `useConnection()`:**

| Поле | Тип | Описание |
|------|-----|----------|
| `address` | `Address \| undefined` | Адрес подключённого кошелька |
| `addresses` | `Address[] \| undefined` | Все адреса (если кошелёк даёт несколько) |
| `chain` | `Chain \| undefined` | Текущая сеть (mainnet, sepolia...) |
| `chainId` | `number \| undefined` | ID сети |
| `connector` | `Connector \| undefined` | Текущий коннектор |
| `status` | `'connecting' \| 'reconnecting' \| 'connected' \| 'disconnected'` | Статус |
| `isConnected` | `boolean` | Удобный флаг |

> **Type narrowing:** когда `status === 'connected'`, поля `address` и `chain` гарантированно определены.

---

### useConnect — подключить кошелёк

В wagmi v3 `useConnect` — это **TanStack Query mutation**. Можно использовать через деструктуризацию `{ connect, connectors }`:

```tsx
import { useConnect, useConnectors } from 'wagmi'

function WalletOptions() {
  const { connect } = useConnect()
  const connectors = useConnectors()

  return (
    <div>
      {connectors.map((connector) => (
        <button key={connector.uid} onClick={() => connect({ connector })}>
          {connector.name}
        </button>
      ))}
    </div>
  )
}
```

**Полный API `useConnect()`:**
- `connect({ connector, chainId? })` — вызвать подключение
- `connectors` (deprecated, используй `useConnectors()`) — список доступных коннекторов
- `isPending`, `isSuccess`, `isError` — статус мутации
- `error` — ошибка подключения
- `data` — `{ accounts, chainId }` после успешного подключения

**Типы коннекторов (из `wagmi/connectors`):**

```ts
import { injected, walletConnect, metaMask, coinbaseWallet, safe } from 'wagmi/connectors'

// injected()      — любой браузерный кошелёк (MetaMask, Brave, Rabby)
// metaMask()      — только MetaMask (EIP-6963)
// walletConnect() — мобильные кошельки через QR-код
// coinbaseWallet()— Coinbase Wallet
// safe()          — Safe (multisig)
```

---

### useBalance — чтение баланса нативного токена

```tsx
import { useBalance, useConnection } from 'wagmi'
import { formatEther } from 'viem'

function Balance() {
  const { address } = useConnection()
  const { data, isError, isLoading } = useBalance({
    address,
  })

  if (isLoading) return <div>Загрузка...</div>
  if (isError) return <div>Ошибка загрузки баланса</div>

  return (
    <div>
      Баланс: {formatEther(data!.value)} {data!.symbol}
    </div>
  )
}
```

> `useBalance` возвращает `{ value: bigint, symbol: string, decimals: number }`. `formatEther()` из viem конвертирует wei (bigint) в читаемую строку.

---

### useReadContract — чтение из смарт-контракта

**Для view/pure функций смарт-контракта.** Не требует газа, работает как TanStack Query.

```tsx
import { useReadContract } from 'wagmi'
import { erc20Abi } from 'viem'

function TokenBalance() {
  const { address } = useConnection()

  const { data: balance } = useReadContract({
    address: '0x6B175474E89094C44Da98b954EedeAC495271d0F', // DAI
    abi: erc20Abi,
    functionName: 'balanceOf',
    args: [address!],
    query: {
      enabled: !!address,  // не запрашивать, пока нет адреса
    },
  })

  return <div>Токенов: {balance?.toString()}</div>
}
```

> **Как читать `useReadContract({ address, abi, functionName, args, query: { enabled: !!address } })`:** «прочитай данные из смарт-контракта React-хуком: вот адрес контракта, вот его ABI-интерфейс, вот какую view-функцию вызвать и с какими аргументами; `enabled: !!address` откладывает запрос до появления кошелька». Мнемоника: `useReadContract` = бесплатный GET в блокчейн через React Query — кэшируется, рефетчится, не платишь газ.

**Подробнее о параметрах:**
- `address` — адрес контракта
- `abi` — ABI контракта (из viem есть готовые: `erc20Abi`, `erc721Abi`)
- `functionName` — имя функции
- `args` — аргументы (типы выводятся из ABI)
- `blockNumber` / `blockTag` — на каком блоке читать
- `account` — адрес для `msg.sender` (опционально)
- `query.enabled` — отключить авто-запрос (полезно, пока нет адреса)

> **Типизация из ABI:** если передать правильно типизированный ABI, TypeScript сам выведет типы аргументов и возвращаемого значения.

---

### useWriteContract — отправка транзакции к контракту

**Для функций, меняющих состояние блокчейна.** Это мутация — требует подтверждения пользователем в кошельке.

```tsx
import { useWriteContract, useWaitForTransactionReceipt } from 'wagmi'
import { erc20Abi } from 'viem'

function TransferToken() {
  const { data: hash, isPending, writeContract } = useWriteContract()

  const { isLoading: isConfirming, isSuccess: isConfirmed } =
    useWaitForTransactionReceipt({ hash })

  return (
    <div>
      <button
        disabled={isPending}
        onClick={() =>
          writeContract({
            address: '0x6B175474E89094C44Da98b954EedeAC495271d0F',
            abi: erc20Abi,
            functionName: 'transfer',
            args: ['0xRecipientAddress...', 1000000000000000000n], // 1 токен в wei
          })
        }
      >
        {isPending ? 'Подтвердите в кошельке...' : 'Отправить 1 DAI'}
      </button>

      {hash && <div>Хеш транзакции: {hash}</div>}
      {isConfirming && <div>Ожидание подтверждения...</div>}
      {isConfirmed && <div>Транзакция подтверждена!</div>}
    </div>
  )
}
```

> **Как читать связку `writeContract({ address, abi, functionName, args })` → `useWaitForTransactionReceipt({ hash })`:** «пошли транзакцию к смарт-контракту — кошелёк запросит подпись, ты получишь хеш; затем передай этот хеш в `useWaitForTransactionReceipt`, чтобы React-хук сам опрашивал сеть и сообщил, когда транзакция попала в блок». Мнемоника: `writeContract` = платный POST → хеш → `useWaitForTransactionReceipt` = жди квитанцию.

> **Паттерн:** `useWriteContract` → получаем `hash` → передаём в `useWaitForTransactionReceipt` → ждём подтверждения.

**Альтернатива — `useWriteContractSync`:** ждёт включения транзакции в блок синхронно (блокирует UI до майнинга). Используй редко.

---

### useWaitForTransactionReceipt — ждать подтверждения

Ждёт, пока транзакция попадёт в блок, и возвращает receipt.

```tsx
import { useWaitForTransactionReceipt } from 'wagmi'

function TransactionStatus({ hash }: { hash: `0x${string}` }) {
  const { data: receipt, isPending, isSuccess, isError, error } =
    useWaitForTransactionReceipt({
      hash,
      confirmations: 2, // ждать 2 блока для надёжности
    })

  if (isPending) return <div>Ожидание...</div>
  if (isError) return <div>Ошибка: {error.message}</div>
  if (isSuccess) return <div>✅ Блок: {receipt.blockNumber.toString()}</div>
}
```

**Параметры:**
- `hash` — хеш транзакции
- `confirmations` — сколько блоков ждать (по умолчанию 1)
- `pollingInterval` — интервал опроса в мс
- `onReplaced` — колбэк, если транзакцию заменили (sped up)

---

### useDisconnect — отключить кошелёк

```tsx
import { useDisconnect } from 'wagmi'

function DisconnectButton() {
  const { disconnect } = useDisconnect()
  return <button onClick={() => disconnect()}>Отключить</button>
}
```

---

### Полезные хуки (краткий справочник)

| Хук | Назначение |
|-----|-----------|
| `useBalance` | Баланс нативного токена (ETH, MATIC...) |
| `useReadContract` | Чтение view-функции контракта |
| `useReadContracts` | Множественное чтение (батч) |
| `useWriteContract` | Отправка транзакции к контракту |
| `useWaitForTransactionReceipt` | Ожидание подтверждения транзакции |
| `useSendTransaction` | Простая отправка ETH (не контракт) |
| `useSignMessage` | Подпись сообщения |
| `useSignTypedData` | Подпись типизированных данных (EIP-712) |
| `useSwitchChain` | Переключение сети |
| `useWatchContractEvent` | Подписка на события контракта |
| `useEnsName` / `useEnsAvatar` | ENS-имена и аватары |
| `useBlockNumber` | Текущий номер блока |
| `useSimulateContract` | Симуляция вызова до отправки |
| `useEstimateGas` | Оценка газа |
| `useChainId` | Текущий chainId |
| `useConnectors` | Список доступных коннекторов |
| `useDisconnect` | Отключение кошелька |

---

## Уровень 2. RainbowKit: готовый UI для Connect Wallet

### Установка

```bash
npm install @rainbow-me/rainbowkit wagmi viem@2.x @tanstack/react-query
```

### Настройка (с getDefaultConfig)

RainbowKit предоставляет `getDefaultConfig()` — обёртку над wagmi `createConfig`, которая автоматически добавляет популярные коннекторы.

```tsx
import '@rainbow-me/rainbowkit/styles.css'
import { getDefaultConfig, RainbowKitProvider } from '@rainbow-me/rainbowkit'
import { WagmiProvider } from 'wagmi'
import { mainnet, sepolia, optimism, arbitrum, base, polygon } from 'wagmi/chains'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const config = getDefaultConfig({
  appName: 'Мой dApp',
  projectId: 'ВАШ_WALLETCONNECT_PROJECT_ID',
  chains: [mainnet, sepolia, optimism, base],
  ssr: true, // если SSR (Next.js)
})

> **Как читать `getDefaultConfig({ appName, projectId, chains, transports?, ssr? })`:** «собери всю конфигурацию RainbowKit одной функцией: имя приложения, WalletConnect ID, список сетей — и получи готовый wagmi-конфиг с автоподключением MetaMask, WalletConnect и Coinbase». Мнемоника: `getDefaultConfig` = `createConfig` + все популярные коннекторы из коробки.

const queryClient = new QueryClient()

function App() {
  return (
    <WagmiProvider config={config}>
      <QueryClientProvider client={queryClient}>
        <RainbowKitProvider>
          {/* Ваше приложение */}
        </RainbowKitProvider>
      </QueryClientProvider>
    </WagmiProvider>
  )
}
```

### ConnectButton — кнопка подключения

```tsx
import { ConnectButton } from '@rainbow-me/rainbowkit'

export default function Header() {
  return (
    <header>
      <h1>Мой dApp</h1>
      <ConnectButton />
    </header>
  )
}
```

**Что даёт ConnectButton из коробки:**
- Кнопка «Connect Wallet» (если не подключён)
- Адрес + аватар + баланс (если подключён)
- Модалка выбора кошелька (MetaMask, WalletConnect, Coinbase...)
- Переключение сети
- Кнопка «Disconnect»

**Кастомизация ConnectButton:**

```tsx
<ConnectButton
  label="Войти"                    // свой текст кнопки
  accountStatus="address"          // только адрес, без аватара
  chainStatus="icon"               // только иконка сети
  showBalance={false}              // скрыть баланс
/>

{/* Адаптивная настройка: */}
<ConnectButton
  accountStatus={{
    smallScreen: 'avatar',         // на телефоне только аватар
    largeScreen: 'full',           // на десктопе адрес + аватар
  }}
  showBalance={{
    smallScreen: false,
    largeScreen: true,
  }}
/>
```

---

### Темы и кастомизация

RainbowKit поставляется с тремя встроенными темами:

```tsx
import { lightTheme, darkTheme, midnightTheme } from '@rainbow-me/rainbowkit'

<RainbowKitProvider theme={darkTheme()}>
```

**Кастомизация темы:**

```tsx
<RainbowKitProvider
  theme={darkTheme({
    accentColor: '#7b3fe4',              // основной цвет
    accentColorForeground: 'white',      // цвет текста на акценте
    borderRadius: 'medium',              // large | medium | small | none
    fontStack: 'system',                 // rounded (default) | system
    overlayBlur: 'small',                // none (default) | small
  })}
>
```

**Готовые пресеты акцентных цветов:**

```tsx
darkTheme({ ...darkTheme.accentColors.pink })
darkTheme({ ...darkTheme.accentColors.green })
darkTheme({ ...darkTheme.accentColors.purple })
darkTheme({ ...darkTheme.accentColors.orange })
darkTheme({ ...darkTheme.accentColors.red })
darkTheme({ ...darkTheme.accentColors.blue })
```

**Поддержка тёмной/светлой темы (авто):**

```tsx
<RainbowKitProvider
  theme={{
    lightMode: lightTheme(),
    darkMode: darkTheme(),
  }}
>
```

---

### Цепочки (chains)

RainbowKit через wagmi поддерживает все EVM-совместимые цепочки из коробки:

```tsx
import {
  mainnet, sepolia, holesky,
  optimism, optimismSepolia,
  arbitrum, arbitrumSepolia,
  base, baseSepolia,
  polygon, polygonMumbai,
  avalanche, avalancheFuji,
  bsc, bscTestnet,
  gnosis, gnosisChiado,
  // ... десятки других
} from 'wagmi/chains'
```

**Добавление кастомной цепи:**

```ts
import { defineChain } from 'viem'

export const myL2 = defineChain({
  id: 12345,
  name: 'My L2',
  nativeCurrency: { name: 'Ether', symbol: 'ETH', decimals: 18 },
  rpcUrls: {
    default: { http: ['https://rpc.myl2.io'] },
  },
  blockExplorers: {
    default: { name: 'MyScan', url: 'https://scan.myl2.io' },
  },
})
```

**Кастомные RPC-провайдеры** (рекомендуется для продакшена):

```ts
const config = getDefaultConfig({
  appName: 'Мой dApp',
  projectId: '...',
  chains: [mainnet, sepolia],
  transports: {
    [mainnet.id]: http('https://eth-mainnet.g.alchemy.com/v2/ВАШ_КЛЮЧ'),
    [sepolia.id]: http('https://eth-sepolia.g.alchemy.com/v2/ВАШ_КЛЮЧ'),
  },
})
```

---

## Уровень 3. viem: низкоуровневые операции

Хотя wagmi покрывает 95% потребностей, иногда нужен прямой доступ к viem. Он уже установлен как зависимость wagmi.

### Чтение баланса (напрямую через viem)

```ts
import { createPublicClient, http, formatEther } from 'viem'
import { mainnet } from 'viem/chains'

const publicClient = createPublicClient({
  chain: mainnet,
  transport: http(),
})

const balance = await publicClient.getBalance({
  address: '0xA0Cf798816D4b9b9866b5330EEa46a18382f251e',
})

console.log(formatEther(balance)) // '6.942'
```

**Через wagmi (рекомендуется):**

```tsx
import { useBalance } from 'wagmi'
// useBalance уже использует publicClient.getBalance под капотом
```

---

### Отправка транзакции (напрямую через viem)

```ts
import { createWalletClient, custom, parseEther } from 'viem'
import { mainnet } from 'viem/chains'

const walletClient = createWalletClient({
  chain: mainnet,
  transport: custom(window.ethereum!),
})

const hash = await walletClient.sendTransaction({
  account: '0x...',
  to: '0x70997970c51812dc3a010c7d01b50e0d17dc79c8',
  value: parseEther('1'), // 1 ETH в wei
})
```

**Через wagmi (рекомендуется):**

```tsx
import { useSendTransaction } from 'wagmi'
import { parseEther } from 'viem'

const { sendTransaction } = useSendTransaction()
sendTransaction({ to: '0x...', value: parseEther('0.01') })
```

---

### viem-утилиты (часто используемые)

```ts
import { formatEther, parseEther, formatUnits, parseUnits } from 'viem'

formatEther(1000000000000000000n)   // '1'
parseEther('1.5')                    // 1500000000000000000n
formatUnits(1000000n, 6)            // '1' (для USDC с 6 decimals)
parseUnits('100', 6)                // 100000000n

// Конвертация адресов
import { getAddress, isAddress } from 'viem'
getAddress('0xa0cf...')             // checksummed address
isAddress('0x...')                   // boolean

// Хеширование
import { keccak256, encodePacked, toHex } from 'viem'
keccak256(toHex('Transfer(address,address,uint256)'))
```

---

### Прямой вызов контракта через viem (если не хватает wagmi)

```ts
import { createPublicClient, http, getContract } from 'viem'
import { erc20Abi } from 'viem'
import { mainnet } from 'viem/chains'

const publicClient = createPublicClient({
  chain: mainnet,
  transport: http(),
})

// Вариант 1: через getContract
const contract = getContract({
  address: '0x6B175474E89094C44Da98b954EedeAC495271d0F',
  abi: erc20Abi,
  client: publicClient,
})
const totalSupply = await contract.read.totalSupply()

// Вариант 2: через readContract напрямую
const balance = await publicClient.readContract({
  address: '0x6B175474E89094C44Da98b954EedeAC495271d0F',
  abi: erc20Abi,
  functionName: 'balanceOf',
  args: ['0x...'],
})
```

---

## Уровень 4. Практический гайд: от Connect Wallet до вызова смарт-контракта

Собираем всё вместе. Создадим dApp, который:
1. Подключает кошелёк (RainbowKit)
2. Показывает баланс ETH (wagmi)
3. Читает баланс ERC-20 токена (wagmi)
4. Отправляет перевод токенов (wagmi)
5. Ждёт подтверждения и показывает результат

### Полный листинг (Next.js App Router)

**1. Установка:**

```bash
npx create-next-app@latest my-dapp
cd my-dapp
npm install @rainbow-me/rainbowkit wagmi viem@2.x @tanstack/react-query
```

**2. `src/config.ts` — конфигурация:**

```ts
import { getDefaultConfig } from '@rainbow-me/rainbowkit'
import { sepolia } from 'wagmi/chains'

export const config = getDefaultConfig({
  appName: 'Мой первый dApp',
  projectId: 'ВАШ_PROJECT_ID',
  chains: [sepolia], // тестовая сеть
  ssr: true,
})
```

**3. `src/app/providers.tsx` — провайдеры (клиентский компонент):**

```tsx
'use client'

import '@rainbow-me/rainbowkit/styles.css'
import { RainbowKitProvider } from '@rainbow-me/rainbowkit'
import { WagmiProvider } from 'wagmi'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { config } from '@/config'
import { useState } from 'react'

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient())

  return (
    <WagmiProvider config={config}>
      <QueryClientProvider client={queryClient}>
        <RainbowKitProvider>
          {children}
        </RainbowKitProvider>
      </QueryClientProvider>
    </WagmiProvider>
  )
}
```

**4. `src/app/layout.tsx` — корневой layout:**

```tsx
import { Providers } from './providers'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
```

**5. `src/app/page.tsx` — главная страница (полный пример):**

```tsx
'use client'

import { ConnectButton } from '@rainbow-me/rainbowkit'
import {
  useConnection,
  useBalance,
  useReadContract,
  useWriteContract,
  useWaitForTransactionReceipt,
} from 'wagmi'
import { erc20Abi, formatEther, parseEther } from 'viem'
import { useState } from 'react'

// Адрес тестового токена в Sepolia (замените на свой)
const TOKEN_ADDRESS = '0x...' as `0x${string}`

function DAppContent() {
  const { address, isConnected } = useConnection()
  const [recipient, setRecipient] = useState('')
  const [amount, setAmount] = useState('')

  // 1. Баланс ETH
  const { data: ethBalance } = useBalance({ address })

  // 2. Баланс токена
  const { data: tokenBalance } = useReadContract({
    address: TOKEN_ADDRESS,
    abi: erc20Abi,
    functionName: 'balanceOf',
    args: address ? [address] : undefined,
    query: { enabled: !!address },
  })

  // 3. Отправка токена
  const {
    data: txHash,
    isPending: isWriting,
    writeContract,
  } = useWriteContract()

  // 4. Ожидание подтверждения
  const {
    isLoading: isConfirming,
    isSuccess: isConfirmed,
  } = useWaitForTransactionReceipt({ hash: txHash })

  if (!isConnected) {
    return (
      <div style={{ textAlign: 'center', marginTop: '20vh' }}>
        <h1>Подключите кошелёк</h1>
        <ConnectButton />
      </div>
    )
  }

  const handleTransfer = () => {
    if (!recipient || !amount) return
    writeContract({
      address: TOKEN_ADDRESS,
      abi: erc20Abi,
      functionName: 'transfer',
      args: [recipient as `0x${string}`, parseEther(amount)],
    })
  }

  return (
    <div style={{ maxWidth: 600, margin: '0 auto', padding: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Мой dApp</h1>
        <ConnectButton />
      </div>

      <div style={{ marginTop: 30 }}>
        <h2>Балансы</h2>
        <p>ETH: {ethBalance ? formatEther(ethBalance.value) : '...'} {ethBalance?.symbol}</p>
        <p>Токен: {tokenBalance ? formatEther(tokenBalance) : '...'}</p>
      </div>

      <div style={{ marginTop: 30 }}>
        <h2>Перевод токенов</h2>
        <input
          placeholder="Адрес получателя (0x...)"
          value={recipient}
          onChange={(e) => setRecipient(e.target.value)}
          style={{ width: '100%', padding: 8, marginBottom: 10 }}
        />
        <input
          placeholder="Количество"
          type="number"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          style={{ width: '100%', padding: 8, marginBottom: 10 }}
        />
        <button
          onClick={handleTransfer}
          disabled={isWriting || !recipient || !amount}
          style={{ padding: '10px 20px', cursor: 'pointer' }}
        >
          {isWriting ? 'Подтвердите в кошельке...' : 'Отправить'}
        </button>
      </div>

      {txHash && (
        <div style={{ marginTop: 20, wordBreak: 'break-all' }}>
          <p>Хеш транзакции: {txHash}</p>
          {isConfirming && <p>⏳ Ожидание подтверждения...</p>}
          {isConfirmed && <p>✅ Транзакция подтверждена!</p>}
        </div>
      )}
    </div>
  )
}

export default function Home() {
  return <DAppContent />
}
```

---

### Блок-схема flow: от клика до confirmed

```
Пользователь нажимает «Подключить»
         │
         ▼
RainbowKit → модалка выбора кошелька
         │
         ▼
Пользователь выбирает MetaMask
         │
         ▼
useConnect → connect({ connector: injected() })
         │
         ▼
useConnection → { isConnected: true, address, chain }
         │
         ▼
Пользователь вводит адрес + сумму → нажимает «Отправить»
         │
         ▼
useWriteContract → writeContract({ address, abi, functionName, args })
         │
         ▼
MetaMask всплывает → пользователь подтверждает транзакцию
         │
         ▼
useWriteContract → возвращает txHash
         │
         ▼
useWaitForTransactionReceipt({ hash: txHash })
         │
    ┌────┴────┐
    ▼         ▼
  success   error
    │         │
    ▼         ▼
isConfirmed  isError
```

---

## Таблица миграции: wagmi v2 → v3

| v2 (старый) | v3 (текущий) |
|-------------|-------------|
| `useAccount()` | `useConnection()` |
| `useConnect({ connector })` | `useConnect()` → `{ connect }`, `connect({ connector })` |
| `useContractRead({ ... })` | `useReadContract({ ... })` |
| `useContractWrite({ ... })` | `useWriteContract()` → `writeContract({ ... })` |
| `useWaitForTransaction({ hash })` | `useWaitForTransactionReceipt({ hash })` |
| Прямой вызов `write()` | `.mutate()` или деструктуризация `{ writeContract }` |
| Не нужен TanStack Query | **Обязателен** `QueryClientProvider` |

> **Проверяйте версию:** `npm list wagmi`. Если v2 — мигрируйте на v3, в v2 больше нет смысла для новых проектов.

---

## Best Practices (из опыта)

1. **`query.enabled: !!address`** — всегда отключайте запросы к контракту, пока нет адреса. Избегает лишних RPC-вызовов.
2. **`useWaitForTransactionReceipt` + `confirmations: 2`** — ждите минимум 2 блока для надёжности.
3. **`useSimulateContract` перед `useWriteContract`** — симулируйте вызов до отправки, чтобы поймать ошибки раньше (экономит газ).
4. **Кастомные RPC для продакшена** — публичные RPC троттлят. Alchemy, Infura, QuickNode.
5. **`ssr: true` в `getDefaultConfig`** если Next.js — избегает hydration mismatch.
6. **Не смешивайте wagmi и прямой viem для одного и того же** — wagmi кэширует запросы через TanStack Query, прямой вызов viem не попадёт в кэш.
7. **ERC-20 ABI из viem** — используйте `erc20Abi` из `viem` вместо ручного написания ABI.
8. **Обработка ошибок:** всегда показывайте `isError` и `error.message` — транзакции могут реджектиться по газу, nonce, slippage.

---

## Частые ошибки

| Ошибка | Причина | Решение |
|--------|---------|---------|
| `Connector not found` | Не настроены connectors в config | Добавьте `injected()`, `walletConnect()` |
| `TypeError: address is undefined` | Хук вызван до подключения кошелька | Добавьте `enabled: !!address` |
| `Missing projectId` | WalletConnect требует projectId | Получите на cloud.walletconnect.com |
| Hydration mismatch (Next.js) | SSR не настроен | `ssr: true` в `getDefaultConfig` |
| `window.ethereum is undefined` | Нет установленного кошелька | Проверьте, что MetaMask установлен |
| `Cannot read properties of undefined (reading 'call')` | ABI не совпадает с контрактом | Проверьте ABI и адрес контракта |

---

## Связанное

- [[wiki/Сравнение-ethers-viem-wagmi]] — сравнение ethers.js, viem и wagmi
- [[wiki/Solidity-основы]] — пишем смарт-контракты, к которым подключается фронтенд
- [[wiki/Главная]] — дорожная карта изучения web3

## Ссылки

- [wagmi.sh](https://wagmi.sh) — документация wagmi
- [rainbowkit.com](https://rainbowkit.com) — документация RainbowKit
- [viem.sh](https://viem.sh) — документация viem
- [WalletConnect Cloud](https://cloud.walletconnect.com) — получить projectId
- [Alchemy](https://alchemy.com) — RPC-провайдер
