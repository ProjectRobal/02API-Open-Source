from os import path
import saml2
import saml2.saml

BASEDIR = path.dirname(path.abspath(__file__))

SAML_CONFIG = {
  # full path to the xmlsec1 binary programm
  'xmlsec_binary': '/usr/bin/xmlsec1',

  # your entity id, usually your subdomain plus the url to the metadata view
  'entityid': 'http://localhost:8000/saml2/metadata/',

  # directory with attribute mapping
  'attribute_map_dir': path.join(BASEDIR, 'attribute-maps'),

  # Permits to have attributes not configured in attribute-mappings
  # otherwise...without OID will be rejected
  'allow_unknown_attributes': True,

  # this block states what services we provide
  'service': {
      # we are just a lonely SP
      'sp' : {
          'name': 'Federated Django sample SP',
          'name_id_format': saml2.saml.NAMEID_FORMAT_TRANSIENT,

          # For Okta add signed logout requests. Enable this:
          # "logout_requests_signed": True,

          'endpoints': {
              # url and binding to the assetion consumer service view
              # do not change the binding or service name
              'assertion_consumer_service': [
                  ('http://localhost:8000/saml2/acs/',
                   saml2.BINDING_HTTP_POST),
                  ],
              # url and binding to the single logout service view
              # do not change the binding or service name
              'single_logout_service': [
                  # Disable next two lines for HTTP_REDIRECT for IDP's that only support HTTP_POST. Ex. Okta:
                  ('http://localhost:8000/saml2/ls/',
                   saml2.BINDING_HTTP_REDIRECT),
                  ('http://localhost:8000/saml2/ls/post',
                   saml2.BINDING_HTTP_POST),
                  ],
              },

          'signing_algorithm':  saml2.xmldsig.SIG_RSA_SHA256,
          'digest_algorithm':  saml2.xmldsig.DIGEST_SHA256,

           # Mandates that the identity provider MUST authenticate the
           # presenter directly rather than rely on a previous security context.
          'force_authn': False,

           # Enable AllowCreate in NameIDPolicy.
          'name_id_format_allow_create': False,

           # attributes that this project need to identify a user
          'required_attributes': ['givenName',
                                  'sn',
                                  'mail'],

           # attributes that may be useful to have but not required
          'optional_attributes': ['eduPersonAffiliation'],

          'want_response_signed': True,
          'authn_requests_signed': True,
          'logout_requests_signed': True,
          # Indicates that Authentication Responses to this SP must
          # be signed. If set to True, the SP will not consume
          # any SAML Responses that are not signed.
          'want_assertions_signed': True,

          'only_use_keys_in_metadata': True,

          # When set to true, the SP will consume unsolicited SAML
          # Responses, i.e. SAML Responses for which it has not sent
          # a respective SAML Authentication Request.
          'allow_unsolicited': False,

          # in this section the list of IdPs we talk to are defined
          # This is not mandatory! All the IdP available in the metadata will be considered instead.
          'idp': {
              # we do not need a WAYF service since there is
              # only an IdP defined here. This IdP should be
              # present in our metadata

              # the keys of this dictionary are entity ids
              'https://localhost/simplesaml/saml2/idp/metadata.php': {
                  'single_sign_on_service': {
                      saml2.BINDING_HTTP_REDIRECT: 'https://localhost/simplesaml/saml2/idp/SSOService.php',
                      },
                  'single_logout_service': {
                      saml2.BINDING_HTTP_REDIRECT: 'https://localhost/simplesaml/saml2/idp/SingleLogoutService.php',
                      },
                  },
              },
          },
      },

  # where the remote metadata is stored, local, remote or mdq server.
  # One metadatastore or many ...
  'metadata': {
      'local': [path.join(BASEDIR, 'remote_metadata.xml')],
      'remote': [{"url": "https://idp.testunical.it/idp/shibboleth"},],
      'mdq': [{"url": "https://ds.testunical.it",
               "cert": "certficates/others/ds.testunical.it.cert",
              }]
      },

  # set to 1 to output debugging information
  'debug': 1,

  # Signing
  'key_file': path.join(BASEDIR, 'private.key'),  # private part
  'cert_file': path.join(BASEDIR, 'public.pem'),  # public part

  # Encryption
  'encryption_keypairs': [{
      'key_file': path.join(BASEDIR, 'private.key'),  # private part
      'cert_file': path.join(BASEDIR, 'public.pem'),  # public part
  }],

  # own metadata settings
  'contact_person': [
      {'given_name': 'Lorenzo',
       'sur_name': 'Gil',
       'company': 'Yaco Sistemas',
       'email_address': 'lorenzo.gil.sanchez@gmail.com',
       'contact_type': 'technical'},
      {'given_name': 'Angel',
       'sur_name': 'Fernandez',
       'company': 'Yaco Sistemas',
       'email_address': 'angel@yaco.es',
       'contact_type': 'administrative'},
      ],
  # you can set multilanguage information here
  'organization': {
      'name': [('Yaco Sistemas', 'es'), ('Yaco Systems', 'en')],
      'display_name': [('Yaco', 'es'), ('Yaco', 'en')],
      'url': [('http://www.yaco.es', 'es'), ('http://www.yaco.com', 'en')],
      },
  }