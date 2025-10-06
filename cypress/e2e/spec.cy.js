describe('App Plania Tests', () => {
  beforeEach(() => {
    cy.visit('http://localhost:5555/')
  })

  it('should load the dashboard', () => {
    cy.get('h1').should('contain', 'Application de Gestion Scolaire') 
  })

  it('the rows should be visible', () => {
    cy.get('.row').should('be.visible')
  })


  describe('The Home Page', () => {
    it('successfully loads planning page', () => {
      cy.visit('/planning')
      // Vérifier que la page se charge correctement
      cy.url().should('include', '/planning')
    })
    
    it('can click on the first button', () => {
      cy.visit('/')
      cy.get('.btn').first().should('be.visible').click()
    })
  })

  describe('The Gestion des Encadrants Page', () => {
    it('successfully loads', () => {
      cy.visit('/planning/gestion-encadrants')
    })
  })
})