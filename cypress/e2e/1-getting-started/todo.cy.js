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
    it('successfully planning', () => {
      cy.visit('/planning')
        // click on the first button
    it('click on the first button', () => {
      cy.get('.btn').first().click()
    })})
  })

  describe('The Gestion des Encadrants Page', () => {
    it('successfully loads', () => {
      cy.visit('/planning/gestion-encadrants')
    })
  })
})