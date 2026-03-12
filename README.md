# Battery Optimizer Light Huawei

<img src="https://raw.githubusercontent.com/awestin67/battery-optimizer-light-huawei/main/custom_components/battery_optimizer_light_huawei/logo.png" alt="Logo" width="200"/>

[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Validate and Test](https://github.com/awestin67/battery-optimizer-light-huawei/actions/workflows/run_tests.yml/badge.svg)](https://github.com/awestin67/battery-optimizer-light-huawei/actions/workflows/run_tests.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

En lättviktig Home Assistant-integration för att styra **Huawei Luna2000-batterier** via den officiella `Huawei Solar`-integrationen.
Fokus ligger på att agera på beslut från Battery Optimizer Light för att styra batteriets laddning/urladdning och driftläge.

## ✨ Funktioner

*   **Sensorer:**
    *   **OBS:** Denna integration skapar inga egna sensorer. Den förlitar sig på de sensorer som tillhandahålls av `Huawei Solar`-integrationen (t.ex. batterinivå, effekt, driftläge).
*   **Styrning:**
    *   🛠 **Tjänster** - `force_charge`, `force_discharge`, `hold` och `auto` för avancerad styrning av Huawei-batteriet. Dessa tjänster anropar i sin tur tjänster i `Huawei Solar`-integrationen.

## 📦 Installation

### Via HACS (Rekommenderas)
1.  Se till att HACS är installerat.
2.  Gå till **HACS** -> **Integrationer**.
3.  Välj menyn (tre prickar) -> **Anpassade arkiv**.
4.  Lägg till URL: `https://github.com/awestin67/battery-optimizer-light-huawei`.
5.  Sök efter "Battery Optimizer Light Huawei" och klicka **Ladda ner**.
6.  Starta om Home Assistant.

### Manuell installation
1.  Ladda ner mappen `battery_optimizer_light_huawei` från detta repo.
2.  Kopiera mappen till `custom_components/` i din Home Assistant-konfiguration.
3.  Starta om Home Assistant.

## ⚙️ Konfiguration

1.  Gå till **Inställningar** -> **Enheter & Tjänster**.
2.  Klicka på **Lägg till integration**.
3.  Sök efter **Battery Optimizer Light Huawei**.
4.  Välj din Huawei Inverter/Batteri-enhet.
5.  Välj entiteten för "Working Mode" (t.ex. `select.inverter_working_mode`).

## Krav
*   En fungerande installation av `Huawei Solar`-integrationen i Home Assistant.
*   Home Assistant 2024.1 eller senare.

## 🛠 Tjänster

Här är de tjänster som integrationen tillhandahåller. Dessa kan anropas via **Utvecklarverktyg -> Tjänster** eller användas i automationer och skript.

### `battery_optimizer_light_huawei.force_charge`
Tvingar batteriet att ladda med en specifik effekt.
*   **Parametrar:**
    *   `power`: (Krävs) Effekten i Watt (W) att ladda med.
*   **Beteende:** Skickar kommando till Huawei-integrationen att tvinga laddning i 60 sekunder.

### `battery_optimizer_light_huawei.force_discharge`
Tvingar batteriet att ladda ur med en specifik effekt.
*   **Parametrar:**
    *   `power`: (Krävs) Effekten i Watt (W) att ladda ur med.
*   **Beteende:** Skickar kommando till Huawei-integrationen att tvinga urladdning i 60 sekunder.

### `battery_optimizer_light_huawei.hold`
Sätter batteriet i vänteläge/paus.
*   **Parametrar:** Inga.
*   **Beteende:** Stoppar eventuell tvingad laddning/urladdning och sätter driftläget till `fixed_charge_discharge` (vilket hindrar batteriet från att ladda ur mot huslasten).

### `battery_optimizer_light_huawei.auto`
Återställer batteriet till automatiskt läge.
*   **Parametrar:** Inga.
*   **Beteende:** Stoppar eventuell tvingad laddning/urladdning och sätter driftläget till `adaptive` (Maximise Self Consumption).

## 🤖 Användning med Battery Optimizer Light

Denna integration är designad för att fungera direkt med [Battery Optimizer Light](https://github.com/awestin67/battery-optimizer-light-ha) och ersätter behovet av manuella `rest_command` och `script` i din `configuration.yaml`.

### Automatisk Styrning

Denna integration lyssnar **automatiskt** på beslut från `Battery Optimizer Light` och styr ditt batteri, vilket eliminerar behovet av en separat automation. Detta är standardbeteendet.

Om du vill stänga av detta och använda egna automationer:
1.  Gå till **Inställningar** -> **Enheter & Tjänster** och klicka på **Konfigurera** för `Battery Optimizer Light Huawei`.
2.  Avmarkera rutan **Enable automatic control**.

Om automatisk styrning är avstängd kan du använda de inbyggda tjänsterna (`force_charge`, `hold`, etc.) i dina egna automationer.
