/**
 * Strategy recommendation system for AITradeStrategist
 * Analyzes historical data and provides trading strategy recommendations
 */

// Strategy templates
const strategyTemplates = {
    // Conservative strategy for low risk
    conservative: {
        id: 'conservative',
        name: 'Conservative Strategy',
        description: 'A low-risk strategy focusing on stable assets with strong fundamentals. ' +
                     'Uses longer timeframes and tighter risk management.',
        riskLevel: 'low',
        expectedReturn: '5-15%',
        successRate: '75-85%',
        params: {
            // Trading parameters
            minimal_roi: {
                "0": 0.07,
                "30": 0.05,
                "60": 0.03
            },
            stoploss: -0.03,
            trailing_stop: true,
            trailing_stop_positive: 0.005,
            trailing_stop_positive_offset: 0.025,
            trailing_only_offset_is_reached: true,
            // Model parameters
            freqai_conf: {
                feature_parameters: {
                    principale_component_analysis: false,
                    use_SVM_to_remove_outliers: true,
                    DI_threshold: 2,
                    use_DBSCAN_to_remove_outliers: false,
                    outlier_protection_percentage: 30
                },
                model_training_parameters: {
                    n_estimators: 400,
                    learning_rate: 0.0025,
                    max_depth: 6,
                    verbosity: 0,
                    boosting_type: "gbdt"
                }
            }
        }
    },
    
    // Balanced strategy for medium risk
    balanced: {
        id: 'balanced',
        name: 'Balanced Strategy',
        description: 'A medium-risk strategy balancing risk and reward. ' +
                     'Suitable for most market conditions with adaptive position sizing.',
        riskLevel: 'medium',
        expectedReturn: '15-25%',
        successRate: '65-75%',
        params: {
            // Trading parameters
            minimal_roi: {
                "0": 0.1,
                "20": 0.07,
                "40": 0.04
            },
            stoploss: -0.05,
            trailing_stop: true,
            trailing_stop_positive: 0.01,
            trailing_stop_positive_offset: 0.02,
            trailing_only_offset_is_reached: true,
            // Model parameters
            freqai_conf: {
                feature_parameters: {
                    principale_component_analysis: true,
                    use_SVM_to_remove_outliers: true,
                    DI_threshold: 1.5,
                    use_DBSCAN_to_remove_outliers: false,
                    outlier_protection_percentage: 20
                },
                model_training_parameters: {
                    n_estimators: 600,
                    learning_rate: 0.005,
                    max_depth: 8,
                    verbosity: 0,
                    boosting_type: "gbdt"
                }
            }
        }
    },
    
    // Aggressive strategy for high risk
    aggressive: {
        id: 'aggressive',
        name: 'Aggressive Growth Strategy',
        description: 'A high-risk strategy targeting substantial returns. ' +
                     'Uses shorter timeframes and more aggressive entry/exit conditions.',
        riskLevel: 'high',
        expectedReturn: '25-40%',
        successRate: '55-65%',
        params: {
            // Trading parameters
            minimal_roi: {
                "0": 0.15,
                "10": 0.1,
                "20": 0.05
            },
            stoploss: -0.08,
            trailing_stop: true,
            trailing_stop_positive: 0.02,
            trailing_stop_positive_offset: 0.03,
            trailing_only_offset_is_reached: false,
            // Model parameters
            freqai_conf: {
                feature_parameters: {
                    principale_component_analysis: true,
                    use_SVM_to_remove_outliers: false,
                    DI_threshold: 1.0,
                    use_DBSCAN_to_remove_outliers: true,
                    outlier_protection_percentage: 10
                },
                model_training_parameters: {
                    n_estimators: 800,
                    learning_rate: 0.01,
                    max_depth: 10,
                    verbosity: 0,
                    boosting_type: "gbdt"
                }
            }
        }
    },
    
    // Trend-following strategy
    trendFollowing: {
        id: 'trendFollowing',
        name: 'Trend Following Strategy',
        description: 'A strategy that focuses on identifying and following established trends. ' +
                     'Works best in trending markets with clear directional movement.',
        riskLevel: 'medium',
        expectedReturn: '20-30%',
        successRate: '60-70%',
        params: {
            // Trading parameters
            minimal_roi: {
                "0": 0.12,
                "30": 0.06,
                "60": 0.03
            },
            stoploss: -0.06,
            trailing_stop: true,
            trailing_stop_positive: 0.015,
            trailing_stop_positive_offset: 0.025,
            trailing_only_offset_is_reached: false,
            // Model parameters
            freqai_conf: {
                feature_parameters: {
                    principale_component_analysis: true,
                    use_SVM_to_remove_outliers: true,
                    DI_threshold: 1.2,
                    use_DBSCAN_to_remove_outliers: false,
                    outlier_protection_percentage: 15
                },
                model_training_parameters: {
                    n_estimators: 700,
                    learning_rate: 0.007,
                    max_depth: 9,
                    verbosity: 0,
                    boosting_type: "gbdt"
                }
            }
        }
    },
    
    // Mean-reversion strategy
    meanReversion: {
        id: 'meanReversion',
        name: 'Mean Reversion Strategy',
        description: 'A strategy that capitalizes on price reversions to the mean. ' +
                     'Effective in ranging markets with oscillating price movements.',
        riskLevel: 'medium',
        expectedReturn: '15-25%',
        successRate: '65-75%',
        params: {
            // Trading parameters
            minimal_roi: {
                "0": 0.08,
                "20": 0.05,
                "40": 0.03
            },
            stoploss: -0.04,
            trailing_stop: true,
            trailing_stop_positive: 0.01,
            trailing_stop_positive_offset: 0.015,
            trailing_only_offset_is_reached: true,
            // Model parameters
            freqai_conf: {
                feature_parameters: {
                    principale_component_analysis: false,
                    use_SVM_to_remove_outliers: true,
                    DI_threshold: 1.8,
                    use_DBSCAN_to_remove_outliers: true,
                    outlier_protection_percentage: 25
                },
                model_training_parameters: {
                    n_estimators: 500,
                    learning_rate: 0.0035,
                    max_depth: 7,
                    verbosity: 0,
                    boosting_type: "gbdt"
                }
            }
        }
    }
};

// Analyze market data and provide strategy recommendations
function analyzeMarketData(marketData, userPreferences = {}) {
    // Default user preferences
    const preferences = {
        riskLevel: userPreferences.riskLevel || 'medium',  // low, medium, high
        returnTarget: userPreferences.returnTarget || 'balanced',  // conservative, balanced, aggressive
        tradingFrequency: userPreferences.tradingFrequency || 'medium',  // low, medium, high
        ...userPreferences
    };
    
    // Market state analysis (simplified example)
    let marketState = {
        trend: null,       // uptrend, downtrend, sideways
        volatility: null,  // low, medium, high
        volume: null       // low, medium, high
    };
    
    try {
        // Calculate market properties based on input data
        if (marketData && marketData.candles && marketData.candles.length > 0) {
            // Detect trend using simple moving averages
            const prices = marketData.candles.map(candle => candle.close);
            const shortMA = calculateSMA(prices, 10);
            const longMA = calculateSMA(prices, 50);
            
            if (shortMA > longMA * 1.02) {
                marketState.trend = 'uptrend';
            } else if (shortMA < longMA * 0.98) {
                marketState.trend = 'downtrend';
            } else {
                marketState.trend = 'sideways';
            }
            
            // Calculate volatility
            const volatility = calculateVolatility(prices, 20);
            marketState.volatility = categorizeVolatility(volatility);
            
            // Calculate volume profile
            if (marketData.candles[0].volume) {
                const volumes = marketData.candles.map(candle => candle.volume);
                const avgVolume = volumes.reduce((sum, vol) => sum + vol, 0) / volumes.length;
                const recentAvgVolume = volumes.slice(-5).reduce((sum, vol) => sum + vol, 0) / 5;
                
                if (recentAvgVolume > avgVolume * 1.5) {
                    marketState.volume = 'high';
                } else if (recentAvgVolume < avgVolume * 0.75) {
                    marketState.volume = 'low';
                } else {
                    marketState.volume = 'medium';
                }
            } else {
                marketState.volume = 'unknown';
            }
        } else {
            // Use default values if no data available
            marketState = {
                trend: 'sideways',
                volatility: 'medium',
                volume: 'medium'
            };
        }
    } catch (error) {
        console.error('Error analyzing market data:', error);
        // Use default values if analysis fails
        marketState = {
            trend: 'sideways',
            volatility: 'medium',
            volume: 'medium'
        };
    }
    
    // Match market state and user preferences to recommended strategies
    const recommendations = generateRecommendations(marketState, preferences);
    
    return {
        marketState,
        recommendations
    };
}

// Generate strategy recommendations based on market state and user preferences
function generateRecommendations(marketState, preferences) {
    const recommendations = [];
    
    // Select primary strategy based on risk level and market state
    let primaryStrategy;
    
    // Conservative risk preference
    if (preferences.riskLevel === 'low') {
        primaryStrategy = strategyTemplates.conservative;
        
        // Secondary recommendations
        if (marketState.trend === 'uptrend' && marketState.volatility !== 'high') {
            recommendations.push(createCustomStrategy(
                strategyTemplates.balanced,
                'Modified Balanced Strategy',
                'A moderately conservative approach for uptrending markets.'
            ));
        }
        
        if (marketState.trend === 'sideways') {
            recommendations.push(createCustomStrategy(
                strategyTemplates.meanReversion,
                'Conservative Mean Reversion',
                'Lower-risk mean reversion strategy for sideways markets.'
            ));
        }
    }
    // Medium risk preference
    else if (preferences.riskLevel === 'medium') {
        if (marketState.trend === 'uptrend') {
            primaryStrategy = strategyTemplates.trendFollowing;
        } else if (marketState.trend === 'sideways') {
            primaryStrategy = strategyTemplates.meanReversion;
        } else {
            primaryStrategy = strategyTemplates.balanced;
        }
        
        // Secondary recommendations
        if (marketState.volatility === 'high') {
            recommendations.push(createCustomStrategy(
                strategyTemplates.conservative,
                'Volatility-Adjusted Conservative',
                'Conservative approach for high volatility conditions.'
            ));
        }
        
        if (marketState.volatility === 'low' && marketState.trend !== 'sideways') {
            recommendations.push(createCustomStrategy(
                strategyTemplates.aggressive,
                'Limited Aggressive Approach',
                'Cautiously aggressive strategy for low volatility trending markets.'
            ));
        }
    }
    // High risk preference
    else {
        primaryStrategy = strategyTemplates.aggressive;
        
        // Secondary recommendations
        if (marketState.trend === 'uptrend') {
            recommendations.push(createCustomStrategy(
                strategyTemplates.trendFollowing,
                'Aggressive Trend Following',
                'High-octane trend following strategy for strong uptrends.'
            ));
        }
        
        if (marketState.volatility === 'high') {
            recommendations.push(createCustomStrategy(
                strategyTemplates.balanced,
                'Volatility-Aware Balanced',
                'More controlled approach for high volatility conditions.'
            ));
        }
    }
    
    // Insert primary strategy at the beginning
    recommendations.unshift(primaryStrategy);
    
    // Add market-specific customization to recommendations
    recommendations.forEach(strategy => {
        // Add market state insights
        strategy.marketInsights = {
            marketState,
            suitability: getSuitabilityScore(strategy, marketState),
            recommendations: getParameterRecommendations(strategy, marketState)
        };
    });
    
    return recommendations;
}

// Create a custom strategy based on a template with modifications
function createCustomStrategy(baseStrategy, name, description, modifications = {}) {
    // Deep clone the base strategy
    const newStrategy = JSON.parse(JSON.stringify(baseStrategy));
    
    // Apply custom properties
    newStrategy.name = name;
    newStrategy.description = description;
    newStrategy.id = 'custom_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
    
    // Apply any parameter modifications
    if (modifications.params) {
        newStrategy.params = { ...newStrategy.params, ...modifications.params };
    }
    
    if (modifications.riskLevel) {
        newStrategy.riskLevel = modifications.riskLevel;
    }
    
    if (modifications.expectedReturn) {
        newStrategy.expectedReturn = modifications.expectedReturn;
    }
    
    if (modifications.successRate) {
        newStrategy.successRate = modifications.successRate;
    }
    
    return newStrategy;
}

// Helper function to calculate Simple Moving Average
function calculateSMA(prices, period) {
    if (prices.length < period) {
        return prices.reduce((sum, price) => sum + price, 0) / prices.length;
    }
    
    return prices.slice(-period).reduce((sum, price) => sum + price, 0) / period;
}

// Helper function to calculate price volatility
function calculateVolatility(prices, period) {
    if (prices.length < 2) return 0;
    
    const priceChanges = [];
    const dataPoints = Math.min(prices.length, period);
    
    for (let i = 1; i < dataPoints; i++) {
        const pctChange = Math.abs((prices[prices.length - i] / prices[prices.length - i - 1]) - 1);
        priceChanges.push(pctChange);
    }
    
    const avgChange = priceChanges.reduce((sum, change) => sum + change, 0) / priceChanges.length;
    
    return avgChange;
}

// Helper function to categorize volatility
function categorizeVolatility(volatility) {
    if (volatility < 0.005) return 'low';
    if (volatility > 0.015) return 'high';
    return 'medium';
}

// Calculate suitability score for a strategy in the current market conditions
function getSuitabilityScore(strategy, marketState) {
    let score = 0;
    
    // Risk level matching
    if (strategy.riskLevel === 'low') {
        score += marketState.volatility === 'high' ? 1 : (marketState.volatility === 'medium' ? 2 : 3);
    } else if (strategy.riskLevel === 'medium') {
        score += marketState.volatility === 'high' ? 2 : (marketState.volatility === 'medium' ? 3 : 2);
    } else {
        score += marketState.volatility === 'high' ? 3 : (marketState.volatility === 'medium' ? 2 : 1);
    }
    
    // Trend matching
    if (strategy.id === 'trendFollowing' || strategy.id.includes('trendFollowing')) {
        score += marketState.trend !== 'sideways' ? 3 : 1;
    } else if (strategy.id === 'meanReversion' || strategy.id.includes('meanReversion')) {
        score += marketState.trend === 'sideways' ? 3 : 1;
    } else if (strategy.id === 'conservative' || strategy.id.includes('conservative')) {
        score += 2; // Generally suitable across market conditions
    }
    
    // Volume consideration
    if (marketState.volume === 'high') {
        score += strategy.riskLevel !== 'low' ? 1 : 0;
    } else if (marketState.volume === 'low') {
        score += strategy.riskLevel === 'low' ? 1 : 0;
    }
    
    // Normalize to 0-10 scale
    return Math.min(Math.max(score, 0), 10);
}

// Get parameter recommendations based on market conditions
function getParameterRecommendations(strategy, marketState) {
    const recommendations = [];
    
    // Stoploss adjustments
    if (marketState.volatility === 'high' && strategy.params.stoploss > -0.05) {
        recommendations.push({
            parameter: 'stoploss',
            currentValue: strategy.params.stoploss,
            recommendedValue: strategy.params.stoploss * 1.2,
            reason: 'Increase stoploss to account for higher volatility'
        });
    }
    
    if (marketState.volatility === 'low' && strategy.params.stoploss < -0.05) {
        recommendations.push({
            parameter: 'stoploss',
            currentValue: strategy.params.stoploss,
            recommendedValue: strategy.params.stoploss * 0.8,
            reason: 'Tighten stoploss in low volatility conditions'
        });
    }
    
    // ROI adjustments
    if (marketState.trend === 'uptrend' && strategy.riskLevel !== 'high') {
        recommendations.push({
            parameter: 'minimal_roi',
            currentValue: strategy.params.minimal_roi,
            recommendedValue: {
                "0": strategy.params.minimal_roi["0"] * 1.1,
                "30": strategy.params.minimal_roi["30"] * 1.1,
                "60": strategy.params.minimal_roi["60"] * 1.1
            },
            reason: 'Increase profit targets in uptrending market'
        });
    }
    
    if (marketState.trend === 'downtrend') {
        recommendations.push({
            parameter: 'minimal_roi',
            currentValue: strategy.params.minimal_roi,
            recommendedValue: {
                "0": strategy.params.minimal_roi["0"] * 0.9,
                "30": strategy.params.minimal_roi["30"] * 0.9,
                "60": strategy.params.minimal_roi["60"] * 0.9
            },
            reason: 'Lower profit targets in downtrending market'
        });
    }
    
    // Trailing stop adjustments
    if (marketState.trend === 'uptrend' && strategy.params.trailing_stop) {
        recommendations.push({
            parameter: 'trailing_stop_positive',
            currentValue: strategy.params.trailing_stop_positive,
            recommendedValue: strategy.params.trailing_stop_positive * 1.2,
            reason: 'Increase trailing stop to capture more profit in uptrends'
        });
    }
    
    return recommendations;
}

// Apply a recommended strategy to the trading system
function applyStrategy(strategy, customizations = {}) {
    // Merge the base strategy with any customizations
    const finalStrategy = {
        ...strategy,
        params: {
            ...strategy.params,
            ...customizations
        }
    };
    
    // In a real implementation, this would send the strategy to the backend
    // For now, we'll just return the strategy object
    console.log('Applying strategy:', finalStrategy);
    
    return {
        success: true,
        message: 'Strategy applied successfully',
        strategy: finalStrategy
    };
}

// Export strategy recommendation functions
window.strategyRecommender = {
    analyzeMarketData,
    applyStrategy,
    getAvailableStrategies: () => Object.values(strategyTemplates)
};