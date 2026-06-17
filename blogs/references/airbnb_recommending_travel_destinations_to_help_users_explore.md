# Recommending Travel Destinations to Help Users Explore

Source: https://airbnb.tech/ai-ml/recommending-travel-destinations-to-help-users-explore/

By: Weiwei Guo, Bin Xu, Sundara Rajan Srinivasavaradhan, Jie Tang, Xiaowei Liu, Bharathi Thangamani, Liwei He, Huiji Gao, Tracy Yu, Hui Gao, Stephanie Moyerman, Sanjeev Katariya

Airbnb users in the trip planning stage may not have a clear idea of travel destinations, travel dates, or other preferences. They exhibit different behaviors compared to users who have a clear itinerary in mind. More exploratory users visit the Airbnb platform less often and are less likely to book listings in the near future; they’re more likely to search for a broad area such as “France” looking for inspiration. We believe that by helping users in the exploration stage, we can spark inspiration, reduce decision friction, and drive improvements in engagement and conversions.

In this blog post, we describe how we help users in the exploration stage by recommending travel destinations. There are multiple unique challenges in modeling destination intent: for example, how to effectively integrate diverse signals (users’ long term interests vs. short term interests), how to balance dormant user behavior vs. active user behavior, and how to encode rich geolocation knowledge.

To address these challenges, we developed a framework that predicts users’ destination intent based on their actions on the Airbnb platform. While the framework is inspired by language modeling, we introduce several key adaptations in training data creation, model architecture, and loss function to tailor it to the destination recommendation problem in the travel domain. Lastly, we present two applications, autosuggest and abandoned search email notifications, that help users explore destination possibilities and facilitate booking decisions.

## Model architecture

Travel destination is one of the primary aspects users explore during trip planning, as it largely determines subsequent decisions such as travel timing, budget, and accommodation preferences. User travel destination preferences are driven by a combination of historical behavior, contextual signals, and temporal factors, etc. For instance, users who previously booked listings in Hawaii may exhibit a preference for beach or tropical destinations, while seasonal context (e.g., summer) may shift their intent toward cooler locations.

In our model, we generalize the destination prediction based on historical user preference data. (Users are able to opt out of this personalization.) As shown in Figure 1, we treat each user action as a token, inspired by language modeling. We use transformers to model sequences of user actions as recorded in various sources: booking history, view history, and search history. Each action is represented by the sum of embeddings of city / region / days to today. We also use contextual information, such as the current time, to capture seasonality. This setup enables the model to summarize user’s short-term interests (views, searches), and long-term interests (bookings), and make a holistic prediction of destination intent.

## Balancing active users and dormant users

At Airbnb, we need to make predictions not only for “active users,” but also for “dormant users”. They exhibit different behaviors, for example:

- **Active users:** User A recently issued a search in the California Bay Area last week. She is currently looking for more affordable listings in the Bay Area.
- **Dormant users:** User B made several bookings in 2025, and hasn’t returned to Airbnb since then. He is currently exploring ideas for a summer vacation in 2026.

Motivated by these two different types of goals, we design the training data shown in Figure 2. For each booking, we create 14 training examples in total. There are two parts:

1. Seven training examples for active users, from 1, 2, 3…7 days before the booking date. For these 7 examples, we use the up-to-date booking/view/search data. This is to mimic the late booking stage when users have a rough idea where to go.
2. Seven training examples for dormant users, randomly sampled from 8 to 365 days before the booking. For these 7 examples, we only use booking data, to mimic the early planning stage when users don’t have a concrete idea and haven’t come to Airbnb.

## Improving location understanding

At Airbnb, we have rich geolocation information about cities and their relationships. For example, the California Bay Area contains many closely related cities; a user interested in staying in San Francisco may also consider nearby cities such as San Jose. For the purposes of destination recommendation, the Bay Area can be viewed as a broader “region” that encompasses multiple cities.

To incorporate this information into our framework, we use multi-task learning. Specifically, we add multiple prediction heads at the final layer of the model, each corresponding to a different prediction task. As shown in Figure 1, the model is trained to predict both the region-level and the city-level destination. By jointly learning these tasks and encouraging consistency between region and city predictions, the model learns richer geolocation representations of cities.

## Applications

We deployed the resulting model in two features of the Airbnb platform. The first is autosuggest. When users click on the search bar, multiple city recommendations are presented. Online A/B testing shows significant booking gains in regions where English is not the primary language; further analysis indicates that these recommendations benefit not only users who have not yet decided on a destination, but also users who are open to booking more affordable listings in neighboring cities.

The second application is abandoned search email notifications. When a user abandons a search on Airbnb, we send follow-up emails featuring listings from areas predicted by the destination recommendation model. This helps drive bookings by encouraging users to explore alternative listings within the recommended destinations and re-engaging them to complete a booking on Airbnb.

## Conclusion

In this post, we described a destination recommendation framework designed to support users in the exploration stage of trip planning, when intent is often ambiguous and preferences are still forming. Our framework includes several key innovations: modeling multiple sequences of user actions to balance short-term and long-term interests, designing training data to accommodate both active and dormant user behaviors, and using multi-task learning to incorporate rich geolocation information. Deployed in autosuggest and abandoned search email notifications, the model helps users discover relevant destination alternatives and drives measurable booking gains. Looking ahead, this framework provides a solid foundation for modeling other preferences, such as travel times and price preferences, enabling broader and deeper personalization across the travel planning journey.
