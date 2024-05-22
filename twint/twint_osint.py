import twint

#configuration
config = twint.Config()
config.Search = "bitcoin"
config.Lang = "en"
config.Limit = 10
#config.Since = "2019–04–29"
#config.Until = "2020–04–29"
config.Store_json = True
config.Output = "custom_out.json"
#running search
twint.run.Search(config)