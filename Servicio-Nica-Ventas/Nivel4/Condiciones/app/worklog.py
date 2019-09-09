class Worklog:

   def __init__(self, dbcon, logger):
       self._dbcon=dbcon
       self._logger=logger

   def find_price(self, sku):
       sql = """
       select * from products  where sku="{}";
       """.format(  
             sku)
       cur = self._dbcon.connection.cursor()
       cur.execute(sql)
       rv = cur.fetchone()
       cur.close()
       return rv

   def find_rules(self, weather, **payload):
       sql = """
       select country
              , city
              , rl.sku
              , min_condition
              , max_condition
              , variation
              , pr.description
              , pr.price
       from rules as rl
       inner join products as pr on rl.sku = pr.sku
       where country = "{}" and city =  "{}" and  min_condition <= "{}" and max_condition >= "{}" and  rl.sku = "{}"; 
       """.format(  
              payload['country'],
              payload['city'],
              weather,
              weather,
              payload['sku'])
       cur = self._dbcon.connection.cursor()
       cur.execute(sql)
       rv = cur.fetchone()
       cur.close()
       self._logger.info(sql)
       self._logger.info(rv)
       return rv

