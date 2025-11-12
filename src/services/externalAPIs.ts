// Integração com APIs externas: clima, cripto, notícias

export interface WeatherData {
  temp: number;
  description: string;
  city: string;
}

export interface CryptoPrice {
  symbol: string;
  price: number;
  change24h: number;
}

export const getWeather = async (city: string = 'Montreal'): Promise<WeatherData | null> => {
  try {
    // wttr.in - API gratuita de clima, sem necessidade de key
    // Formato JSON: https://wttr.in/Montreal?format=j1
    const response = await fetch(
      `https://wttr.in/${encodeURIComponent(city)}?format=j1`,
      { 
        headers: { 
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
          'Accept': 'application/json'
        }
      }
    );

    if (response.ok) {
      const data = await response.json();
      const current = data.current_condition?.[0];
      
      if (current) {
        return {
          temp: parseInt(current.temp_C) || 0,
          description: current.weatherDesc?.[0]?.value || 'N/A',
          city: data.nearest_area?.[0]?.areaName?.[0]?.value || city,
        };
      }
    }

    return null;
  } catch (error) {
    console.error('Error fetching weather:', error);
    return null;
  }
};

export const getCryptoPrice = async (symbol: string = 'BTC'): Promise<CryptoPrice | null> => {
  try {
    // CoinGecko API (gratuita, sem key)
    const response = await fetch(
      `https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true`
    );

    if (response.ok) {
      const data = await response.json();
      const coinId = symbol === 'BTC' ? 'bitcoin' : 'ethereum';
      const coinData = data[coinId];
      
      if (coinData) {
        return {
          symbol,
          price: coinData.usd,
          change24h: coinData.usd_24h_change || 0,
        };
      }
    }

    return null;
  } catch (error) {
    console.error('Error fetching crypto:', error);
    return null;
  }
};

export const formatWeatherInfo = (weather: WeatherData): string => {
  return `Clima em ${weather.city}: ${weather.temp}°C, ${weather.description}`;
};

export const formatCryptoInfo = (crypto: CryptoPrice): string => {
  const change = crypto.change24h >= 0 ? '+' : '';
  return `${crypto.symbol}: $${crypto.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} (${change}${crypto.change24h.toFixed(2)}% 24h)`;
};

