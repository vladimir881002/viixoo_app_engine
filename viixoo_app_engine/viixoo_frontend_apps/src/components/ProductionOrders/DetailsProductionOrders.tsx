import {
  Button,
  ButtonGroup,
  DialogActionTrigger,
  VStack,
  Tabs,
  Input,
  Table,
  Box,
} from "@chakra-ui/react"
import { useState } from "react"
import { GrView } from "react-icons/gr";

import type { ProductionOrderPublic } from "../../client/types.gen"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"


interface ProductionOrderProps {
  item: ProductionOrderPublic
}

export const DetailsProductionOrder = ({ item }: ProductionOrderProps) => {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button size="xs" colorPalette="gray" variant="ghost">
          <GrView fontSize="16px" />
          Detalles
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form>
          <DialogHeader>
            <DialogTitle>Orden de fabricación</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <VStack gap={4}>
              <Field
                label="Referencia:"
              >
                 <Input
                    id="name"
                    type="text"
                    defaultValue={item?.name || ""}
                    readOnly
                  >
                  </Input>
              </Field>

              <Field
                label="Producto:"
              >
                <Input
                    id="product"
                    type="text"
                    defaultValue={item?.product || ""}
                    readOnly
                  >
                  </Input>
              </Field>
              <Field
                label="Cantidad:"
              >
                <Input
                    id="product_qty"
                    type="text"
                    defaultValue={item?.product_qty || ""}
                    readOnly
                  >
                  </Input>
              </Field>
              <Field
                label="Lista de materiales:"
              >
              </Field>
              <Field
                label="Fecha inicio:"
              >
                <Input
                    id="date_start"
                    type="text"
                    defaultValue={item?.date_start || ""}
                    readOnly
                  >
                  </Input>
              </Field>
              <Field
                label="Fecha fin:"
              >
                 <Input
                    id="date_finished"
                    type="text"
                    defaultValue={item?.date_finished || ""}
                    readOnly
                  >
                  </Input>

              </Field>
              <Tabs.Root defaultValue="work-order" variant="subtle">
                <Tabs.List>
                    <Tabs.Trigger key="1" value="work-order">
                    Órdenes de trabajo
                    </Tabs.Trigger>
                    <Tabs.Trigger key="2" value="list-components">
                    Lista de componentes
                    </Tabs.Trigger>
                </Tabs.List>
               <Tabs.Content key="1" value="work-order">
                <Box maxH="100px" overflowY="auto" borderWidth="1px" borderRadius="md">
                    <Table.Root maxH="100px" size="sm" showColumnBorder>
                      <Table.Header>
                        <Table.Row>
                          <Table.ColumnHeader w="sm">Referencia</Table.ColumnHeader>
                          <Table.ColumnHeader w="sm">Producto</Table.ColumnHeader>
                          <Table.ColumnHeader w="sm">Cantidad a producir</Table.ColumnHeader>
                        </Table.Row>
                      </Table.Header>
                      <Table.Body>
                        {item.workorder_ids?.map((workorder) => (
                          <Table.Row key={workorder.workorder_id}>
                            <Table.Cell truncate maxW="sm">
                              {workorder.name}
                            </Table.Cell>
                            <Table.Cell truncate maxW="sm">
                              {workorder.product}
                            </Table.Cell>
                            <Table.Cell truncate maxW="30%">
                              {workorder.qty_remaining}
                            </Table.Cell>
                          </Table.Row>
                        ))}
                      </Table.Body>
                    </Table.Root>
                  </Box>
                </Tabs.Content>
                <Tabs.Content key="2" value="list-components">
                  <Box maxH="100px" overflowY="auto" borderWidth="1px" borderRadius="md">
                    <Table.Root maxH="100px" size="sm" showColumnBorder>
                      <Table.Header>
                        <Table.Row>
                          <Table.ColumnHeader fontWeight="bold" w="sm">Producto</Table.ColumnHeader>
                          <Table.ColumnHeader fontWeight="bold" w="sm">Cantidad</Table.ColumnHeader>
                        </Table.Row>
                      </Table.Header>
                      <Table.Body>
                        {item.move_raw_ids?.map((comp) => (
                          <Table.Row key={comp.move_raw_id}>
                            <Table.Cell truncate maxW="sm">
                              {comp.product}
                            </Table.Cell>
                            <Table.Cell truncate maxW="30%">
                              {comp.quantity}
                            </Table.Cell>
                          </Table.Row>
                        ))}
                      </Table.Body>
                    </Table.Root>
                  </Box>
                </Tabs.Content>
              </Tabs.Root>
            </VStack>
          </DialogBody>

          <DialogFooter gap={2}>
            <ButtonGroup>
              <DialogActionTrigger asChild>
                <Button
                  variant="subtle"
                  colorPalette="gray"
                >
                  Cerrar
                </Button>
              </DialogActionTrigger>
            </ButtonGroup>
          </DialogFooter>
        </form>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}
