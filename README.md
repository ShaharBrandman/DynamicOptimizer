## How to run?

## execution: python3 run.py
## configuration:

# `run.json`

The optimizer can be seprated into three components which its own settings each

# 1. Strategy

which takes the strategy params with input

params can be configured like this:
```
{
    "Strategy": {
        "Params": {
            "FirstMovingAverage": {
                "min": 0.0,
                "max": 200.0
            },
            "SecondMovingAverage: {
                "min": 0.0,
                "max: 200.0
            }
        }
        
    }
}
```
just make sure to set the correct params for your strategy

also we to refrence our data to optimzie with

we can retrieve data Yahoo Finance just like we would use the `yFinance` python module:
```
{
    "Strategy": {
        "Params": {
           ...
        }
        "yFinance": {
            "pair" "BTC-USD",
            "period" "60d", #1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
            "interval" "5m" #1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        }
    }
}
```
make sure to adjust the maximum period to each interval unit

we can also use datasets from other domains using `DatasetURL` keyword
`public.bybit.com` offers lots of data from their exchange like kline
we can import it like this
(The optimizer does have a builtin bybit client)
```
{
    "Strategy": {
        ...
        "DatasetURL": "https://public.bybit.com/kline_for_metatrader4/BTCUSDT/2023/BTCUSDT_15_2023-05-01_2023-05-31.csv.gz"
    }
}
```

or we can import datasets from our file system like that:
```
{
    "Strategy": {
        ...
        "DatasetPath": "~/Desktop/Dataset.csv"
    }
}
```

## 2. Optimizer

after the strategy configuration we'll need to adjust the optimizer to our needs
the run json should look like this:
```
{
    "Strategy": {
        ...
    },
    "Optimizer": {
        "initPoints": 15, How many steps of random exploration you want to perform, the more steps the more diversified exploration space
        "nIter": 300, #How many steps of bayesian optimization you want to perform
        "maximize": ["Return [%]"] #Can be every result param of the `backtesting.py` python module
    }
}
```

it is optional to load previos progress from our file system using the `loadFrom` keyword:
(Only json files are compatible as of BayesianOptimization v1.4.3)
```
{
    "Strategy": {
        ...
    },
    "Optimizer": {
        ...
        "loadFrom": "~/Desktop/progress.json"
    }
}
```

## 3. Portofolio

just like this

but be sure that the commision price is not too high relevant to ur equity
will generate levatating or out of place entry prices
as of backtesting v0.3.3
```
{
    "Strategy": {
        ...
    },
    "Optimizer": {
        ...
    },
    "Portfolio": {
        "Equity": 100000,
        "Leverage": 1,
        "Commision": 0.00025
    }
}
```