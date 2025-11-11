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
    // Usando OpenWeatherMap (requer API key, mas vamos fazer fallback)
    // Por enquanto, retornamos dados mockados ou fazemos requisição direta
    const response = await fetch(
      `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=demo&units=metric`
    ).catch(() => null);

    if (response?.ok) {
      const data = await response.json();
      return {
        temp: data.main.temp,
        description: data.weather[0].description,
        city: data.name,
      };
    }

    // Fallback: retornar null (o SuperEzio pode informar que precisa de API key)
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

