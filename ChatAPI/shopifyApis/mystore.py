import os,json,base64
import re

import httpx
os.environ["NO_PROXY"] = "baidu.com, google.com"

class shopify_utils(object):

    token = "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"
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": f"{token}",
        "User-Agent": "Mozilla/5.0 (Linux; U; Android 8.0.0; zh-cn; Mi Note 2 Build/OPR1.170623.032) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/61.0.3163.128 Mobile Safari/537.36 XiaoMi/MiuiBrowser/10.1.1",
    }
    mystore_url = 'https://6bd16b.myshopify.com/'
    timeout = 5

    @classmethod
    def get_all_users(cls):
        """
        获取所有用户
        :return: res
        """
        users_url = cls.mystore_url+'admin/api/2023-04/customers.json'
        res = httpx.get(users_url, headers=cls.headers,timeout=cls.timeout).json()
        return res

    @classmethod
    def get_all_products(cls,username=None,Type=None):
        """
        获取所有产品
        :return: res
        """
        items = cls.get_order_count()
        # 第一页请求
        # page = 1
        limit = 250
        products_url = cls.mystore_url + f"admin/api/2023-04/products.json?limit={limit}"
        res = httpx.get(products_url, headers=cls.headers,timeout=cls.timeout)
        # print(res.json())
        products = res.json()['products']

        # print(res.headers)
        # # 获取所有产品
        # while 'link' in res.headers:
        #     next_page_url = re.findall('<(.+?)>',res.headers['link'])[0]
        #     print(next_page_url)
        #     response = httpx.get(next_page_url, headers=cls.headers,timeout=cls.timeout)
        #     products += response.json()['products']

        # print(products)

        user_products_data = []
        if Type == 0:
            for j in products:
                print(j)
                if j['product_type'] == "Ai":
                    detail_url = cls.mystore_url +f'admin/api/2023-04/products/{str(j["id"])}/metafields.json'
                    rs = httpx.get(detail_url, headers=cls.headers, timeout=cls.timeout).json()
                    flag = False
                    for i in rs["metafields"]:
                        if i['key'] == 'create_by' and i['value'] == username:
                            flag = True
                    if flag == True:
                        j['TeamPrice'] = '0.0'
                        j['Rebate'] = '0.0'
                        j['Number'] = items.get(str(j["id"]),0)
                        for i in rs["metafields"]:
                            if i['key'] == 'TeamPrice':
                                j['TeamPrice'] = i.get('value','0.0')
                            if i['key'] == 'rebate':
                                j['Rebate'] = i.get('value', '0.0')
                            if i['key'] == "number":
                                j['Number'] = i.get('value', 0)
                        user_products_data.append(j)
            return user_products_data
        elif Type == 1:
            for j in products:
                if j['product_type'] == 'Ai' and j['status'] == 'active':
                    detail_url = cls.mystore_url +f'admin/api/2023-04/products/{str(j["id"])}/metafields.json'
                    rs = httpx.get(detail_url, headers=cls.headers, timeout=cls.timeout).json()
                    j['TeamPrice'] = '0.0'
                    j['Rebate'] = '0.0'
                    j['Number'] = items.get(str(j["id"]),0)
                    for i in rs["metafields"]:
                        if i['key'] == 'TeamPrice':
                            j['TeamPrice'] = i.get('value', '0.0')
                        if i['key'] == 'rebate':
                            j['Rebate'] = i.get('value', '0.0')
                        if i['key'] == "number":
                            j['Number'] = i.get('value', 0)
                    user_products_data.append(j)
        return user_products_data

    @classmethod
    def add_product(cls,username=None,productType=None,filename=None):
        """
        添加商品
        :return: res
        """
        # data = {
        #     "product":{"title":"mycc","body_html":"<strong>Good snowboard!</strong>","vendor":"Mindi","product_type":"Ai","status":"draft","create_by":"2326520660@qq.com"},
        #     "published": True,
        #     "published_scope": "web",
        # }
        product_data = {
            "product": {
                "title": "Gallery generated products",
                "body_html": "<p>This is the product description.</p>",
                "product_type": "Ai",
                "vendor":"Mindi",
                "variants": [
                    {
                        "title": "Default",
                        "price": "9.99",
                        "sku": "SKU123",
                        "inventory_quantity": 10,
                        "inventory_management": "shopify",
                        "fulfillment_service": "manual"
                    }
                ],
                "options": [
                    {
                        "name": "Size",
                        "values": [
                            "Small",
                            "Medium",
                            "Large"
                        ]
                    }
                ],
                "published": True,
                "published_scope": "web",
                "status": "draft",
            }
        }
        products_url = cls.mystore_url+"admin/api/2023-04/products.json"
        res = httpx.post(products_url, headers=cls.headers,timeout=cls.timeout,json=product_data).json()
        cls.add_product_images(res['product']['id'],filename)
        ## 修改元字段的信息
        wsproduct = {
            "operationName": "MetafieldsSet",
            "variables": {
                "metafields": [{
                    "namespace": "product",
                    "key": "create_by",
                    "type": "single_line_text_field",
                    "value": username,
                    "ownerId": "gid://shopify/Product/" + str(res['product']['id'])
                },
                    {
                        "namespace": "product",
                        "key": "source",
                        "type": "single_line_text_field",
                        "value": "Ai",
                        "ownerId": "gid://shopify/Product/" + str(res['product']['id'])
                    },
                    {
                        "namespace": "product",
                        "key": "type",
                        "type": "single_line_text_field",
                        "value": productType,
                        "ownerId": "gid://shopify/Product/" + str(res['product']['id'])
                    },
                    {
                        "namespace": "product",
                        "key": "TeamPrice",
                        "type": "number_decimal",
                        "value": "0.0",
                        "ownerId": "gid://shopify/Product/" + str(res['product']['id'])
                    },
                    {
                        "namespace": "product",
                        "key": "Rebate",
                        "type": "number_decimal",
                        "value": "0.0",
                        "ownerId": "gid://shopify/Product/" + str(res['product']['id'])
                    }
                ]
            },
            "query": "mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {\n  metafieldsSet(metafields: $metafields) {\n    metafields {\n      id\n      namespace\n      key\n      value\n      __typename\n    }\n    userErrors {\n      field\n      message\n      elementIndex\n      __typename\n    }\n    __typename\n  }\n}\n"
        }
        url = cls.mystore_url+'admin/api/2023-04/graphql.json'
        httpx.post(url,headers=cls.headers, timeout=cls.timeout, data=json.dumps(wsproduct)).json()

    @classmethod
    def update_idcard(cls,username=None,idcard=None):
        # 获取所有的用户
        result = cls.get_all_users()
        user_id = None
        for i in result['customers']:
            if i['email'] == username:
                user_id = i['id']
                break
        if user_id == None:
            return {"statu": False,"message":"There is no such user!"}
        else:
            endpoint = cls.mystore_url+f'admin/api/2023-04/customers/{user_id}/metafields.json'
            # Create a new metafield payload
            payload = {
                "metafield": {
                    "key": "idcard",
                    "value": idcard,
                    "type": "single_line_text_field",
                    "namespace": "custom"
                }
            }
            httpx.post(endpoint, headers=cls.headers, timeout=cls.timeout, data=json.dumps(payload)).json()
            return {"statu": True,"message":"Account updated successfully!"}

    @classmethod
    def add_product_images(cls,product_id=None,filepath=None):
        """
        增加产品图
        :return: res
        """
        img_b64 = cls.encode_base64(filepath)
        images_url = cls.mystore_url+'admin/api/2023-04/products/{}/images.json'.format(product_id)
        send_data = json.dumps({"image":{"position":1,"metafields":[{"key":"new","value":"newvalue","type":"single_line_text_field","namespace":"global"}],"attachment":img_b64,"filename":"my_logo.jpg"}})
        res = httpx.post(images_url, headers=cls.headers,timeout=cls.timeout,data=send_data).json()
        return res

    @classmethod
    def get_order_count(cls):

        """
        获取产品的数量
        :return: res
        """
        url = "https://6bd16b.myshopify.com/admin/api/2023-04/orders.json?status=any&limit=250"
        response = httpx.get(url,headers=cls.headers, timeout=cls.timeout)

        # 第一页请求
        orders = response.json()['orders']
        # 获取所有订单
        # while 'nextPage' in response.headers:
        #     next_page_url = response.headers['nextPage']
        #     response = httpx.get(next_page_url, headers=cls.headers, timeout=cls.timeout)
        #     orders += response.json()['orders']
        # return response.json()
        if response.status_code == 200:
            # orders = response.json()['orders']
            product_sales = {}  # 用于存储每个商品的销售数量
            for order in orders:
                line_items = order['line_items']
                for item in line_items:
                    product_title = item['product_id']
                    quantity = item['quantity']
                    if product_title in product_sales:
                        product_sales[product_title] += quantity
                    else:
                        product_sales[product_title] = quantity
            # 更新订单id打印每个商品的销售数量
            items = {}
            for product, sales in product_sales.items():
                items[str(product)] = sales
                # print(f"Product: {product}, Sales: {sales}")
            return items
        else:
            print('Failed to retrieve order data')

    # @classmethod
    # def get_cumster(cls):
    #     url = cls.mystore_url+"/admin/api/2023-04/metafields.json"
    #     response = httpx.get(url,headers=cls.headers, timeout=cls.timeout)
    #     print(response.json()['metafields'])


    @classmethod
    def queryTypes(cls):
        """
        查找产品产品的类别！
        :return:
        """
        # data ={
        #     "query": "mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) { metafieldDefinitionCreate(definition: $definition) { createdDefinition { id name } userErrors { field message code } } }",
        #      "variables": {
        #          "definition": {
        #              "name": "Imgs",
        #              "namespace": "custom",
        #              "key": "imgs",
        #              "description": "A list of ingredients used to make the product.",
        #              "type": "single_line_text_field",
        #              "ownerType": "CUSTOMER",
        #          }
        #       }
        #     }
        # data = {
        #     "operationName": "MetaobjectIndex",
        #     "variables": {
        #         "query": "type:product",
        #         "definitionCount": 64,
        #         "first": 50,
        #         "referenceCount": 10,
        #         "sortKey": "updated_at",
        #         "reverse": False
        #     },
        #     "query": "query MetaobjectIndex($query: String, $first: Int, $last: Int, $before: String, $after: String, $definitionCount: Int, $referenceCount: Int, $sortKey: String, $reverse: Boolean, $savedSearchId: ID) {\n  metaobjectDefinitions(first: $definitionCount, reverse: true) {\n    edges {\n      node {\n        id\n        type\n        name\n        metaobjectsCount\n        metaobjectsWriteAccess\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  metaobjects: allMetaobjects(\n    first: $first\n    last: $last\n    before: $before\n    after: $after\n    query: $query\n    reverse: $reverse\n    sortKey: $sortKey\n    savedSearchId: $savedSearchId\n  ) {\n    edges {\n      cursor\n      node {\n        id\n        displayName\n        handle\n        capabilities {\n          publishable {\n            status\n            __typename\n          }\n          __typename\n        }\n        type\n        updatedAt\n        definition {\n          id\n          name\n          access {\n            storefront\n            admin\n            __typename\n          }\n          capabilities {\n            publishable {\n              enabled\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        referencedBy(first: $referenceCount) {\n          edges {\n            cursor\n            __typename\n          }\n          pageInfo {\n            hasNextPage\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    pageInfo {\n      hasPreviousPage\n      hasNextPage\n      __typename\n    }\n    __typename\n  }\n}\n"
        # }
        data = {
            "operationName": "MetaobjectIndex",
            "variables": {
                "query": "type:product",
                "definitionCount": 64,
                "first": 50,
                "referenceCount": 10,
                "sortKey": "updated_at",
            },
                "query": "query MetaobjectIndex($query: String, $first: Int, $last: Int, $before: String, $after: String, $definitionCount: Int, $referenceCount: Int, $sortKey: String, $reverse: Boolean, $savedSearchId: ID) {\n  metaobjectDefinitions(first: $definitionCount, reverse: true) {\n    edges {\n      node {\n        id\n        type\n        name\n        metaobjectsCount\n        metaobjectsWriteAccess\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  metaobjects: allMetaobjects(\n    first: $first\n    last: $last\n    before: $before\n    after: $after\n    query: $query\n    reverse: $reverse\n    sortKey: $sortKey\n    savedSearchId: $savedSearchId\n  ) {\n    edges {\n      cursor\n      node {\n        id\n        displayName\n        handle\n        capabilities {\n          publishable {\n            status\n            __typename\n          }\n          __typename\n        }\n        type\n        updatedAt\n        definition {\n          id\n          name\n          access {\n            storefront\n            admin\n            __typename\n          }\n          capabilities {\n            publishable {\n              enabled\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        referencedBy(first: $referenceCount) {\n          edges {\n            cursor\n            __typename\n          }\n          pageInfo {\n            hasNextPage\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    pageInfo {\n      hasPreviousPage\n      hasNextPage\n      __typename\n    }\n    __typename\n  }\n}\n"
            }
        ## 插入邮箱和
        yzdurl = "https://6bd16b.myshopify.com/admin/api/2023-04/graphql.json"
        res = httpx.post(yzdurl, headers=cls.headers, timeout=cls.timeout,data=json.dumps(data)).json()
        # print(res)

    @classmethod
    def encode_base64(cls,file):
        with open(file, 'rb') as f:
            img_data = f.read()
            base64_data = base64.b64encode(img_data)
            # print(base64_data)
            # 如果想要在浏览器上访问base64格式图片，需要在前面加上：data:image/jpeg;base64,
            base64_str = str(base64_data, 'utf-8')
            return base64_str

    @classmethod
    def decode_base64(cls,base64_data):
        with open('./images/base64.jpg', 'wb') as file:
            img = base64.b64decode(base64_data)
            file.write(img)


if __name__ == '__main__':
#     # print(shopify_utils.add_product_images('8436976386350','../images/2.png'))
#     # print(shopify_utils.add_product("2326520660@qq.com","shop",'./wx.png'))
#
    # print(shopify_utils.get_all_products("2326520333@qq.com",0))
#     # print()
#
#     # '/admin/api/2021-04/products/8390574997806/variants.json'
#
    print(shopify_utils.get_order_count())
#
#     # print(shopify_utils.get_cumster())
#







